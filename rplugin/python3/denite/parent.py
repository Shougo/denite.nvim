# ============================================================================
# FILE: parent.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================


class _Parent(object):
    def __init__(self, vim):
        self.name = 'parent'

        self._vim = vim

        self._start_process()

    def start(self, context):
        self._put('start', [context])

    def gather_candidates(self, context):
        self._put('gather_candidates', [context])

    def on_init(self, context):
        self._put('on_init', [context])

    def on_close(self, context):
        self._put('on_close', [context])

    def init_syntax(self, context, is_multi):
        self._put('init_syntax', [context, is_multi])

    def filter_candidates(self, context):
        return self._put('filter_candidates', [context])

    def do_action(self, context, action_name, targets):
        return self._put('do_action', [context, action_name, targets])

    def get_action(self, context, action_name, targets):
        return self._put('get_action', [context, action_name, targets])

    def get_action_names(self, context, targets):
        return self._put('get_action_names', [context, targets])

    def is_async(self):
        return self._put('is_async', [])


class SyncParent(_Parent):
    def _start_process(self):
        from denite.child import Child
        self._child = Child(self._vim)

    def _put(self, name, args):
        return self._child.main(name, args, queue_id=None)
