# ============================================================================
# FILE: map.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import debug, clear_cmdline
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
    return denite._restart()


def _change_sorters(denite, params):
    sorters = ''.join(params)
    context = denite._context
    if context['sorters'] != sorters:
        context['sorters'] = sorters
    else:
        context['sorters'] = ''
    return denite.redraw()


def _choose_action(denite, params):
    candidates = denite._get_selected_candidates()
    if not candidates:
        return

    denite._vim.vars['denite#_actions'] = denite._denite.get_action_names(
        denite._context, candidates)
    clear_cmdline(denite._vim)
    action = denite._vim.call('input', 'Action: ', '',
                              'customlist,denite#helper#complete_actions')
    if action == '':
        return
    return denite.do_action(action)


def _do_action(denite, params):
    name = params[0] if params else 'default'
    return denite.do_action(name)


def _do_previous_action(denite, params):
    return denite.do_action(denite._prev_action)


def _filter(denite, params):
    text = params[0] if params else ''

    denite._context['input'] = text

    if denite._update_candidates():
        denite._update_buffer()
    else:
        denite._update_status()

    if denite._previous_text != text:
        denite._previous_text = text
        denite._init_cursor()
        denite._move_to_pos(denite._cursor)


def _move_up_path(denite, params):
    denite._context['path'] = dirname(denite._context['path'])
    return denite._restart()


def _nop(denite, params):
    pass


def _open_filter_buffer(denite, params):
    denite._vim.call('denite#filter#open',
                     denite._context, denite._bufnr,
                     denite._entire_len, denite.is_async)


def _print_messages(denite, params):
    for mes in denite._context['messages']:
        debug(denite._vim, mes)
    denite._vim.call('denite#util#getchar')


def _quick_move(denite, params):
    def get_quick_move_table():
        table = {}
        context = denite._context
        base = denite._vim.call('line', '.')
        for [key, number] in context['quick_move_table'].items():
            number = int(number)
            pos = ((base - number) if context['reversed']
                   else (number + base))
            if pos > 0:
                table[key] = pos
        return table

    def quick_move_redraw(table, is_define):
        bufnr = denite._vim.current.buffer.number
        for [key, number] in table.items():
            signid = 2000 + number
            name = 'denite_quick_move_' + str(number)
            if is_define:
                denite._vim.command(
                    f'sign define {name} text={key} texthl=Special')
                denite._vim.command(
                    f'sign place {signid} name={name} '
                    f'line={number} buffer={bufnr}')
            else:
                denite._vim.command(
                    f'silent! sign unplace {signid} buffer={bufnr}')
                denite._vim.command('silent! sign undefine ' + name)

    quick_move_table = get_quick_move_table()
    denite._vim.command('echo "Input quick match key: "')
    quick_move_redraw(quick_move_table, True)
    denite._vim.command('redraw')

    char = ''
    while char == '':
        char = denite._vim.call('nr2char',
                                denite._vim.call('denite#util#getchar'))

    quick_move_redraw(quick_move_table, False)

    if char not in quick_move_table:
        return

    denite._move_to_pos(int(quick_move_table[char]))

    if denite._context['quick_move'] == 'immediately':
        denite.do_action('default')
        return True


def _quit(denite, params):
    return denite.quit()


def _redraw(denite, params):
    return denite.redraw()


def _restart(denite, params):
    return denite._restart()


def _restore_sources(denite, params):
    if not denite._sources_history:
        return

    history = denite._sources_history[-1]
    denite._context['sources_queue'].append(history['sources'])
    denite._context['path'] = history['path']
    denite._sources_history.pop()


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
    return denite._update_buffer()


def _toggle_select_candidate(denite, index):
    if index in denite._selected_candidates:
        denite._selected_candidates.remove(index)
    else:
        denite._selected_candidates.append(index)


def _toggle_select_all(denite, params):
    for index in range(0, denite._candidates_len):
        _toggle_select_candidate(denite, index)
    denite.update_displayed_texts()
    return denite._update_buffer()


def _update(denite, params):
    if not denite.is_async:
        return

    if denite._update_candidates():
        denite._update_buffer()
    else:
        denite._update_status()


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
