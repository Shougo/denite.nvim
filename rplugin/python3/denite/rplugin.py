# https://github.com/lambdalisue/vim-rplugin/pytyhon3/rplugin.py
import vim


# NOTE:
# vim.options['encoding'] returns bytes so use vim.eval('&encoding')
ENCODING = vim.eval('&encoding')


def reform_bytes(value):
    if isinstance(value, bytes):
        return value.decode(ENCODING, 'surrogateescape')
    elif isinstance(value, (dict, vim.Dictionary, vim.Options)):
        return {
            reform_bytes(k): reform_bytes(v) for k, v in value.items()
        }
    elif isinstance(value, (list, tuple, vim.List)):
        return list(map(reform_bytes, value))
    elif value is None:
        return 0
    else:
        return value


class Proxy:
    def __init__(self, component):
        self._component = component
        self.__class__ = build_proxy(self, component)

    def __getattr__(self, name):
        value = getattr(self._component, name)
        return decorate(value)


class ContainerProxy(Proxy):
    def __getitem__(self, key):
        return reform_bytes(self._component[key])

    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = value.encode(ENCODING, 'surrogateescape')
        self._component[key] = value


class FuncNamespace:
    __slots__ = ['vim']

    def __init__(self, vim):
        self.vim = vim

    def __getattr__(self, name):
        fn = self.vim.Function(name)
        return lambda *args: reform_bytes(fn(*args))


class Neovim(Proxy):
    def __init__(self, vim):
        self.funcs = FuncNamespace(vim)
        super().__init__(vim)

    def call(self, name, *args):
        return reform_bytes(self.Function(name)(*args))


def build_proxy(child, parent):
    proxy = type(
        "%s:%s" % (
            type(parent).__name__,
            child.__class__.__name__,
        ),
        (child.__class__,), {}
    )
    child_class = child.__class__
    parent_class = parent.__class__

    def bind(attr):
        if hasattr(child_class, attr) or not hasattr(parent_class, attr):
            return

        ori = getattr(parent_class, attr)

        def mod(self, *args, **kwargs):
            return ori(self._component, *args, **kwargs)

        setattr(proxy, attr, mod)

    for attr in parent_class.__dict__.keys():
        bind(attr)

    return proxy


def decorate(component):
    if component in (vim.buffers, vim.windows, vim.tabpages, vim.current):
        return Proxy(component)
    elif isinstance(component, (vim.Buffer, vim.Window, vim.TabPage)):
        return Proxy(component)
    elif isinstance(component, (vim.List, vim.Dictionary, vim.Options)):
        return ContainerProxy(component)
    return component
