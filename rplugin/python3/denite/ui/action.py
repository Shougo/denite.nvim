import re
from datetime import timedelta, datetime

from denite.util import debug
from os.path import dirname
from denite.prompt.util import build_keyword_pattern_set


def _redraw(prompt, params):
    return prompt.denite.redraw()


def _quit(prompt, params):
    return prompt.denite.quit()


def _do_action(prompt, params):
    return prompt.denite.do_action(params)


def _do_previous_action(prompt, params):
    return prompt.denite.do_action(prompt.denite._prev_action)


def _choose_action(prompt, params):
    return prompt.denite.choose_action()


def _move_to_next_line(prompt, params):
    for cnt in range(0, _accel_count(prompt.denite)):
        prompt.denite.move_to_next_line()
    return prompt.denite.move_to_next_line()


def _move_to_previous_line(prompt, params):
    for cnt in range(0, _accel_count(prompt.denite)):
        prompt.denite.move_to_prev_line()
    return prompt.denite.move_to_prev_line()


def _accel_count(denite):
    if not denite._context['auto_accel']:
        return 0
    now = datetime.now()
    if not hasattr(denite, '_accel_timeout'):
        denite._accel_timeout = now
    timeout = denite._accel_timeout
    denite._accel_timeout = now + timedelta(milliseconds=100)
    return 2 if timeout > now else 0


def _move_to_top(prompt, params):
    return prompt.denite.move_to_top()


def _move_to_middle(prompt, params):
    return prompt.denite.move_to_middle()


def _move_to_bottom(prompt, params):
    return prompt.denite.move_to_bottom()


def _move_to_first_line(prompt, params):
    return prompt.denite.move_to_first_line()


def _move_to_last_line(prompt, params):
    return prompt.denite.move_to_last_line()


def _scroll_window_upwards(prompt, params):
    return prompt.denite.scroll_window_upwards()


def _scroll_window_up_one_line(prompt, params):
    return prompt.denite.scroll_window_up_one_line()


def _scroll_window_downwards(prompt, params):
    return prompt.denite.scroll_window_downwards()


def _scroll_window_down_one_line(prompt, params):
    return prompt.denite.scroll_window_down_one_line()


def _scroll_page_forwards(prompt, params):
    return prompt.denite.scroll_page_forwards()


def _scroll_page_backwards(prompt, params):
    return prompt.denite.scroll_page_backwards()


def _scroll_up(prompt, params):
    return prompt.denite.scroll_up(int(params))


def _scroll_down(prompt, params):
    return prompt.denite.scroll_down(int(params))


def _scroll_cursor_to_top(prompt, params):
    return prompt.denite.scroll_cursor_to_top()


def _scroll_cursor_to_middle(prompt, params):
    return prompt.denite.scroll_cursor_to_middle()


def _scroll_cursor_to_bottom(prompt, params):
    return prompt.denite.scroll_cursor_to_bottom()


def _jump_to_next_by(prompt, params):
    return prompt.denite.jump_to_next_by(params)


def _jump_to_previous_by(prompt, params):
    return prompt.denite.jump_to_prev_by(params)


def _jump_to_next_source(prompt, params):
    return prompt.denite.jump_to_next_by('source_name')


def _jump_to_previous_source(prompt, params):
    return prompt.denite.jump_to_prev_by('source_name')


def _input_command_line(prompt, params):
    prompt.nvim.command('redraw | echo')
    text = prompt.nvim.call('input', prompt.prefix)
    prompt.update_text(text)


def _insert_word(prompt, params):
    prompt.update_text(params)


def _enter_mode(prompt, params):
    return prompt.denite.enter_mode(params)


def _leave_mode(prompt, params):
    return prompt.denite.leave_mode()


def _suspend(prompt, params):
    return prompt.denite.suspend()


def _wincmd(prompt, params):
    mapping = {
            'h': 'wincmd h',
            'j': 'wincmd j',
            'k': 'wincmd k',
            'l': 'wincmd l',
            'w': 'wincmd w',
            'W': 'wincmd W',
            't': 'wincmd t',
            'b': 'wincmd b',
            'p': 'wincmd p',
            'P': 'wincmd P',
            }
    if params not in mapping:
        return
    ret = prompt.denite.suspend()
    prompt.nvim.command(mapping[params])
    return ret


def _restart(prompt, params):
    return prompt.denite.restart()


def _restore_sources(prompt, params):
    return prompt.denite.restore_sources(prompt.denite._context)


def _toggle_select(prompt, params):
    index = prompt.denite._cursor + prompt.denite._win_cursor - 1
    _toggle_select_candidate(prompt, index)
    prompt.denite.update_displayed_texts()
    return prompt.denite.update_buffer()


def _toggle_select_candidate(prompt, index):
    if index in prompt.denite._selected_candidates:
        prompt.denite._selected_candidates.remove(index)
    else:
        prompt.denite._selected_candidates.append(index)


def _toggle_select_all(prompt, params):
    for index in range(0, prompt.denite._candidates_len):
        _toggle_select_candidate(prompt, index)
    prompt.denite.update_displayed_texts()
    return prompt.denite.update_buffer()


def _toggle_select_down(prompt, params):
    _toggle_select(prompt, params)
    return prompt.denite.move_to_next_line()


def _toggle_select_up(prompt, params):
    _toggle_select(prompt, params)
    return prompt.denite.move_to_prev_line()


def _toggle_matchers(prompt, params):
    matchers = ''.join(params)
    context = prompt.denite._context
    if context['matchers'] != matchers:
        context['matchers'] = matchers
    else:
        context['matchers'] = ''
    return prompt.denite.redraw()


def _change_sorters(prompt, params):
    sorters = ''.join(params)
    context = prompt.denite._context
    if context['sorters'] != sorters:
        context['sorters'] = sorters
    else:
        context['sorters'] = ''
    return prompt.denite.redraw()


def _print_messages(prompt, params):
    for mes in prompt.denite._context['messages']:
        debug(prompt.nvim, mes)
    prompt.nvim.call('denite#util#getchar')


def _change_path(prompt, params):
    path = prompt.nvim.call('input', 'Path: ',
                            prompt.denite._context['path'], 'dir')
    prompt.denite._context['path'] = path
    return prompt.denite.restart()


def _move_up_path(prompt, params):
    prompt.denite._context['path'] = dirname(prompt.denite._context['path'])
    return prompt.denite.restart()


def _change_word(prompt, params):
    # NOTE: Respect the behavior of 'w' in Normal mode.
    if prompt.caret.locus == prompt.caret.tail:
        return prompt.denite.change_mode('insert')
    pattern_set = build_keyword_pattern_set(prompt.nvim)
    pattern = re.compile(
        r'^(?:%s+|%s+|[^\s\x20-\xff]+|)\s*' % pattern_set
    )
    forward_text = pattern.sub('', prompt.caret.get_forward_text())
    prompt.text = ''.join([
        prompt.caret.get_backward_text(),
        forward_text
    ])
    prompt.denite.change_mode('insert')


def _change_line(prompt, params):
    prompt.text = ''
    prompt.caret.locus = 0
    prompt.denite.change_mode('insert')


def _change_char(prompt, params):
    prompt.text = ''.join([
        prompt.caret.get_backward_text(),
        prompt.caret.get_forward_text(),
    ])
    prompt.denite.change_mode('insert')


def _move_caret_to_next_word(prompt, params):
    pattern = re.compile(r'^\S+\s+\S')
    original_text = prompt.caret.get_forward_text()
    substituted_text = pattern.sub('', original_text)
    prompt.caret.locus += len(original_text) - len(substituted_text)


def _move_caret_to_end_of_word(prompt, params):
    pattern = re.compile(r'^\S+')
    original_text = prompt.caret.get_forward_text()
    if original_text and original_text[0] == ' ':
        _move_caret_to_next_word(prompt, params)
        _move_caret_to_end_of_word(prompt, params)
    else:
        substituted_text = pattern.sub('', original_text)
        prompt.caret.locus += len(original_text) - len(substituted_text)


def _append(prompt, params):
    prompt.caret.locus += 1
    prompt.denite.change_mode('insert')


def _append_to_line(prompt, params):
    prompt.caret.locus = prompt.caret.tail
    prompt.denite.change_mode('insert')


def _insert_to_head(prompt, params):
    prompt.caret.locus = prompt.caret.head
    prompt.denite.change_mode('insert')


def _quick_move(prompt, params):
    prompt.denite.quick_move()


def _multiple_mappings(prompt, params):
    ret = None
    for mapping in params.split(','):
        ret = prompt.action.call(prompt, mapping)
    return ret


def _smart_delete_char_before_caret(prompt, params):
    text = ''.join([
        prompt.caret.get_backward_text(),
        prompt.caret.get_forward_text(),
    ])
    if text:
        return prompt.action.call(prompt, 'denite:delete_char_before_caret')
    else:
        return _quit(prompt, params)


def _nop(prompt, params):
    pass


DEFAULT_ACTION_RULES = [
    ('denite:append', _append),
    ('denite:append_to_line', _append_to_line),
    ('denite:change_char', _change_char),
    ('denite:change_line', _change_line),
    ('denite:change_path', _change_path),
    ('denite:change_sorters', _change_sorters),
    ('denite:change_word', _change_word),
    ('denite:choose_action', _choose_action),
    ('denite:do_action', _do_action),
    ('denite:do_previous_action', _do_previous_action),
    ('denite:enter_mode', _enter_mode),
    ('denite:input_command_line', _input_command_line),
    ('denite:insert_to_head', _insert_to_head),
    ('denite:insert_word', _insert_word),
    ('denite:jump_to_next_by', _jump_to_next_by),
    ('denite:jump_to_next_source', _jump_to_next_source),
    ('denite:jump_to_previous_by', _jump_to_previous_by),
    ('denite:jump_to_previous_source', _jump_to_previous_source),
    ('denite:leave_mode', _leave_mode),
    ('denite:move_caret_to_end_of_word', _move_caret_to_end_of_word),
    ('denite:move_caret_to_next_word', _move_caret_to_next_word),
    ('denite:move_to_bottom', _move_to_bottom),
    ('denite:move_to_first_line', _move_to_first_line),
    ('denite:move_to_last_line', _move_to_last_line),
    ('denite:move_to_middle', _move_to_middle),
    ('denite:move_to_next_line', _move_to_next_line),
    ('denite:move_to_previous_line', _move_to_previous_line),
    ('denite:move_to_top', _move_to_top),
    ('denite:move_up_path', _move_up_path),
    ('denite:multiple_mappings', _multiple_mappings),
    ('denite:nop', _nop),
    ('denite:print_messages', _print_messages),
    ('denite:quick_move', _quick_move),
    ('denite:quit', _quit),
    ('denite:redraw', _redraw),
    ('denite:restart', _restart),
    ('denite:restore_sources', _restore_sources),
    ('denite:scroll_cursor_to_bottom', _scroll_cursor_to_bottom),
    ('denite:scroll_cursor_to_middle', _scroll_cursor_to_middle),
    ('denite:scroll_cursor_to_top', _scroll_cursor_to_top),
    ('denite:scroll_down', _scroll_down),
    ('denite:scroll_page_backwards', _scroll_page_backwards),
    ('denite:scroll_page_forwards', _scroll_page_forwards),
    ('denite:scroll_up', _scroll_up),
    ('denite:scroll_window_down_one_line', _scroll_window_down_one_line),
    ('denite:scroll_window_downwards', _scroll_window_downwards),
    ('denite:scroll_window_up_one_line', _scroll_window_up_one_line),
    ('denite:scroll_window_upwards', _scroll_window_upwards),
    ('denite:smart_delete_char_before_caret',
     _smart_delete_char_before_caret),
    ('denite:suspend', _suspend),
    ('denite:toggle_matchers', _toggle_matchers),
    ('denite:toggle_select', _toggle_select),
    ('denite:toggle_select_all', _toggle_select_all),
    ('denite:toggle_select_down', _toggle_select_down),
    ('denite:toggle_select_up', _toggle_select_up),
    ('denite:wincmd', _wincmd),
]

DEFAULT_ACTION_KEYMAP = {
    '_': [
        ('<Esc>', '<denite:leave_mode>', 'noremap'),
        ('<CR>', '<denite:do_action:default>', 'noremap'),
        ('<C-M>', '<denite:do_action:default>', 'noremap'),
        ('<C-Z>', '<denite:suspend>', 'noremap'),
        ('<Tab>', '<denite:choose_action>', 'noremap'),
    ],
    'insert': [
        # Behave like Vim's builtin command-line
        ('<C-B>', '<denite:move_caret_to_head>', 'noremap'),
        ('<C-E>', '<denite:move_caret_to_tail>', 'noremap'),
        ('<BS>', '<denite:delete_char_before_caret>', 'noremap'),
        ('<C-H>', '<denite:delete_char_before_caret>', 'noremap'),
        ('<C-K>', '<denite:insert_digraph>', 'noremap'),
        ('<C-N>', '<denite:assign_next_text>', 'noremap'),
        ('<C-P>', '<denite:assign_previous_text>', 'noremap'),
        ('<C-Q>', '<denite:insert_special>', 'noremap'),
        ('<C-R>', '<denite:paste_from_register>', 'noremap'),
        ('<C-U>', '<denite:delete_entire_text>', 'noremap'),
        ('<C-W>', '<denite:delete_word_before_caret>', 'noremap'),
        ('<DEL>', '<denite:delete_char_under_caret>', 'noremap'),
        ('<Left>', '<denite:move_caret_to_left>', 'noremap'),
        ('<S-Left>', '<denite:move_caret_to_one_word_left>', 'noremap'),
        ('<C-Left>', '<denite:move_caret_to_one_word_left>', 'noremap'),
        ('<Right>', '<denite:move_caret_to_right>', 'noremap'),
        ('<S-Right>', '<denite:move_caret_to_one_word_right>', 'noremap'),
        ('<C-Right>', '<denite:move_caret_to_one_word_right>', 'noremap'),
        ('<Up>', '<denite:assign_previous_matched_text>', 'noremap'),
        ('<S-Up>', '<denite:assign_previous_text>', 'noremap'),
        ('<Down>', '<denite:assign_next_matched_text>', 'noremap'),
        ('<S-Down>', '<denite:assign_next_text>', 'noremap'),
        ('<Home>', '<denite:move_caret_to_head>', 'noremap'),
        ('<End>', '<denite:move_caret_to_tail>', 'noremap'),
        ('<PageDown>', '<denite:assign_next_text>', 'noremap'),
        ('<PageUp>', '<denite:assign_previous_text>', 'noremap'),
        ('<INSERT>', '<denite:toggle_insert_mode>', 'noremap'),
        # Denite specific actions
        ('<C-G>', '<denite:move_to_next_line>', 'noremap'),
        ('<C-T>', '<denite:move_to_previous_line>', 'noremap'),
        ('<C-L>', '<denite:redraw>', 'noremap'),
        ('<C-O>', '<denite:enter_mode:normal>', 'noremap'),
        ('<C-J>', '<denite:input_command_line>', 'noremap'),
        ('<C-V>', '<denite:do_action:preview>', 'noremap'),
    ],
    'normal': [
        ('i', '<denite:enter_mode:insert>', 'noremap'),
        ('j', '<denite:move_to_next_line>', 'noremap'),
        ('k', '<denite:move_to_previous_line>', 'noremap'),
        ('gg', '<denite:move_to_first_line>', 'noremap'),
        ('G', '<denite:move_to_last_line>', 'noremap'),
        ('H', '<denite:move_to_top>', 'noremap'),
        ('L', '<denite:move_to_bottom>', 'noremap'),
        ('<C-U>', '<denite:scroll_window_upwards>', 'noremap'),
        ('<C-Y>', '<denite:scroll_window_up_one_line>', 'noremap'),
        ('<C-D>', '<denite:scroll_window_downwards>', 'noremap'),
        ('<C-E>', '<denite:scroll_window_down_one_line>', 'noremap'),
        ('<C-F>', '<denite:scroll_page_forwards>', 'noremap'),
        ('<C-B>', '<denite:scroll_page_backwards>', 'noremap'),
        ('zt', '<denite:scroll_cursor_to_top>', 'noremap'),
        ('zz', '<denite:scroll_cursor_to_middle>', 'noremap'),
        ('zb', '<denite:scroll_cursor_to_bottom>', 'noremap'),
        ('q', '<denite:quit>', 'noremap'),
        ('<C-L>', '<denite:redraw>', 'noremap'),
        ('<C-R>', '<denite:restart>', 'noremap'),
        ('<Space>', '<denite:toggle_select_down>', 'noremap'),
        ('.', '<denite:do_previous_action>', 'noremap'),
        ('*', '<denite:toggle_select_all>', 'noremap'),
        ('M', '<denite:print_messages>', 'noremap'),
        ('P', '<denite:change_path>', 'noremap'),
        ('U', '<denite:move_up_path>', 'noremap'),
        ('b', '<denite:move_caret_to_one_word_left>', 'noremap'),
        ('w', '<denite:move_caret_to_next_word>', 'noremap'),
        ('0', '<denite:move_caret_to_head>', 'noremap'),
        ('u', '<denite:restore_sources>', 'noremap'),
        ('$', '<denite:move_caret_to_tail>', 'noremap'),
        ('cc', '<denite:change_line>', 'noremap'),
        ('S', '<denite:change_line>', 'noremap'),
        ('cw', '<denite:change_word>', 'noremap'),
        ('S', '<denite:change_line>', 'noremap'),
        ('s', '<denite:change_char>', 'noremap'),
        ('x', '<denite:delete_char_under_caret>', 'noremap'),
        ('h', '<denite:move_caret_to_left>', 'noremap'),
        ('l', '<denite:move_caret_to_right>', 'noremap'),
        ('a', '<denite:append>', 'noremap'),
        ('A', '<denite:append_to_line>', 'noremap'),
        ('I', '<denite:insert_to_head>', 'noremap'),
        ('X', '<denite:quick_move>', 'noremap'),
        ('<ScrollWheelUp>', '<denite:scroll_window_up_one_line>', 'noremap'),
        ('<ScrollWheelDown>', '<denite:scroll_window_downwards>', 'noremap'),
        ('<TScrollWheelUp>', '<denite:scroll_window_up_one_line>', 'noremap'),
        ('<TScrollWheelDown>', '<denite:scroll_window_downwards>', 'noremap'),

        # Denite specific actions
        ('e', '<denite:do_action:edit>', 'noremap'),
        ('p', '<denite:do_action:preview>', 'noremap'),
        ('d', '<denite:do_action:delete>', 'noremap'),
        ('n', '<denite:do_action:new>', 'noremap'),
        ('t', '<denite:do_action:tabopen>', 'noremap'),
        ('y', '<denite:do_action:yank>', 'noremap'),
        ('<C-w>h', '<denite:wincmd:h>', 'noremap'),
        ('<C-w>j', '<denite:wincmd:j>', 'noremap'),
        ('<C-w>k', '<denite:wincmd:k>', 'noremap'),
        ('<C-w>l', '<denite:wincmd:l>', 'noremap'),
        ('<C-w>w', '<denite:wincmd:w>', 'noremap'),
        ('<C-w>W', '<denite:wincmd:W>', 'noremap'),
        ('<C-w>t', '<denite:wincmd:t>', 'noremap'),
        ('<C-w>b', '<denite:wincmd:b>', 'noremap'),
        ('<C-w>p', '<denite:wincmd:p>', 'noremap'),
        ('<C-w>P', '<denite:wincmd:P>', 'noremap'),
    ],
}
