# ============================================================================
# FILE: map.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import debug
from os.path import dirname


def do_map(denite, name, params):
    if name not in MAPPINGS:
        return
    return MAPPINGS[name](denite, params)


def _auto_action(denite, params):
    if not denite._context['auto_action']:
        return
    return denite.do_action(denite._context['auto_action'])


def _change_path(denite, params):
    path = denite._vim.call('input', 'Path: ',
                            denite._context['path'], 'dir')
    denite._context['path'] = path
    return denite.restart()


def _change_sorters(denite, params):
    sorters = ''.join(params)
    context = denite._context
    if context['sorters'] != sorters:
        context['sorters'] = sorters
    else:
        context['sorters'] = ''
    return denite.redraw()


def _choose_action(denite, params):
    return denite.choose_action()


def _do_action(denite, params):
    name = params[0] if params else 'default'
    return denite.do_action(name)


def _do_previous_action(denite, params):
    return denite.do_action(denite._prev_action)


def _filter(denite, params):
    text = params[0] if params else ''

    denite._context['input'] = text

    if denite.update_candidates():
        denite.update_buffer()
    else:
        denite.update_status()

    if denite._previous_text != text:
        denite._previous_text = text
        denite.init_cursor()


def _move_up_path(denite, params):
    denite._context['path'] = dirname(denite._context['path'])
    return denite.restart()


def _nop(denite, params):
    pass


def _open_filter_buffer(denite, params):
    denite._vim.call('denite#filter#open',
                     denite._bufnr, denite._context['input'])


def _print_messages(denite, params):
    for mes in denite._context['messages']:
        debug(denite._vim, mes)
    denite._vim.call('denite#util#getchar')


def _quick_move(denite, params):
    denite.quick_move()


def _quit(denite, params):
    return denite.quit()


def _redraw(denite, params):
    return denite.redraw()


def _restart(denite, params):
    return denite.restart()


def _restore_sources(denite, params):
    return denite.restore_sources(denite._context)


def _toggle_matchers(denite, params):
    matchers = ''.join(params)
    context = denite._context
    if context['matchers'] != matchers:
        context['matchers'] = matchers
    else:
        context['matchers'] = ''
    return denite.redraw()


def _toggle_select(denite, params):
    index = denite._vim.call('line', '.') - 1
    _toggle_select_candidate(denite, index)
    denite.update_displayed_texts()
    return denite.update_buffer()


def _toggle_select_candidate(denite, index):
    if index in denite._selected_candidates:
        denite._selected_candidates.remove(index)
    else:
        denite._selected_candidates.append(index)


def _toggle_select_all(denite, params):
    for index in range(0, denite._candidates_len):
        _toggle_select_candidate(denite, index)
    denite.update_displayed_texts()
    return denite.update_buffer()


def _update(denite, params):
    if not denite.is_async:
        return

    if denite.update_candidates():
        denite.update_buffer()
    else:
        denite.update_status()


MAPPINGS = {
    'auto_action': _auto_action,
    'change_path': _change_path,
    'change_sorters': _change_sorters,
    'choose_action': _choose_action,
    'do_action': _do_action,
    'do_previous_action': _do_previous_action,
    'filter': _filter,
    'move_up_path': _move_up_path,
    'nop': _nop,
    'open_filter_buffer': _open_filter_buffer,
    'print_messages': _print_messages,
    'quick_move': _quick_move,
    'quit': _quit,
    'redraw': _redraw,
    'restart': _restart,
    'restore_sources': _restore_sources,
    'toggle_matchers': _toggle_matchers,
    'toggle_select': _toggle_select,
    'toggle_select_all': _toggle_select_all,
    'update': _update,
}
