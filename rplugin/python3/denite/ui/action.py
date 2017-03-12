import re
from denite.util import debug
from denite.prompt.util import build_keyword_pattern_set


def _redraw(prompt, params):
    return prompt.denite.redraw()


def _quit(prompt, params):
    return prompt.denite.quit()


def _do_action(prompt, params):
    return prompt.denite.do_action(params)


def _choose_action(prompt, params):
    return prompt.denite.choose_action()


def _move_to_next_line(prompt, params):
    return prompt.denite.move_to_next_line()


def _move_to_previous_line(prompt, params):
    return prompt.denite.move_to_prev_line()


def _move_to_first_line(prompt, params):
    return prompt.denite.move_to_first_line()


def _move_to_last_line(prompt, params):
    return prompt.denite.move_to_last_line()


def _scroll_window_upwards(prompt, params):
    return prompt.denite.scroll_window_upwards()


def _scroll_window_downwards(prompt, params):
    return prompt.denite.scroll_window_downwards()


def _scroll_page_forwards(prompt, params):
    return prompt.denite.scroll_page_forwards()


def _scroll_page_backwards(prompt, params):
    return prompt.denite.scroll_page_backwards()


def _scroll_up(prompt, params):
    return prompt.denite.scroll_up(int(params))


def _scroll_down(prompt, params):
    return prompt.denite.scroll_down(int(params))


def _jump_to_next_source(prompt, params):
    return prompt.denite.jump_to_next_source()


def _jump_to_previous_source(prompt, params):
    return prompt.denite.jump_to_prev_source()


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


def _restart(prompt, params):
    return prompt.denite.restart()


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


def _print_messages(prompt, params):
    for mes in prompt.denite._context['messages']:
        debug(prompt.nvim, mes)


def _change_path(prompt, params):
    path = prompt.nvim.call('input', 'Path: ',
                            prompt.denite._context['path'], 'dir')
    prompt.denite._context['path'] = path
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


def _move_caret_to_next_word(prompt, params):
    pattern = re.compile('^\S+\s+\S')
    original_text = prompt.caret.get_forward_text()
    substituted_text = pattern.sub('', original_text)
    prompt.caret.locus += len(original_text) - len(substituted_text)


def _move_caret_to_end_of_word(prompt, params):
    pattern = re.compile('^\S+')
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


DEFAULT_ACTION_RULES = [
    ('denite:change_path', _change_path),
    ('denite:choose_action', _choose_action),
    ('denite:do_action', _do_action),
    ('denite:enter_mode', _enter_mode),
    ('denite:input_command_line', _input_command_line),
    ('denite:insert_word', _insert_word),
    ('denite:jump_to_next_source', _jump_to_next_source),
    ('denite:jump_to_previous_source', _jump_to_previous_source),
    ('denite:leave_mode', _leave_mode),
    ('denite:move_to_first_line', _move_to_first_line),
    ('denite:move_to_last_line', _move_to_last_line),
    ('denite:move_to_next_line', _move_to_next_line),
    ('denite:move_to_previous_line', _move_to_previous_line),
    ('denite:quit', _quit),
    ('denite:redraw', _redraw),
    ('denite:restart', _restart),
    ('denite:scroll_down', _scroll_down),
    ('denite:scroll_page_backwards', _scroll_page_backwards),
    ('denite:scroll_page_forwards', _scroll_page_forwards),
    ('denite:scroll_up', _scroll_up),
    ('denite:scroll_window_downwards', _scroll_window_downwards),
    ('denite:scroll_window_upwards', _scroll_window_upwards),
    ('denite:suspend', _suspend),
    ('denite:print_messages', _print_messages),
    ('denite:toggle_select', _toggle_select),
    ('denite:toggle_select_down', _toggle_select_down),
    ('denite:toggle_select_up', _toggle_select_up),
    ('denite:toggle_select_all', _toggle_select_all),
    ('denite:move_caret_to_next_word', _move_caret_to_next_word),
    ('denite:move_caret_to_end_of_word', _move_caret_to_end_of_word),
    ('denite:change_word', _change_word),
    ('denite:change_line', _change_line),
    ('denite:append', _append),
    ('denite:append_to_line', _append_to_line),
    ('denite:insert_to_head', _insert_to_head),
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
        ('<C-U>', '<denite:scroll_window_upwards>', 'noremap'),
        ('<C-D>', '<denite:scroll_window_downwards>', 'noremap'),
        ('<C-F>', '<denite:scroll_page_forwards>', 'noremap'),
        ('<C-B>', '<denite:scroll_page_backwards>', 'noremap'),
        ('q', '<denite:quit>', 'noremap'),
        ('<C-L>', '<denite:redraw>', 'noremap'),
        ('<C-R>', '<denite:restart>', 'noremap'),
        ('<Space>', '<denite:toggle_select_down>', 'noremap'),
        ('*', '<denite:toggle_select_all>', 'noremap'),
        ('M', '<denite:print_messages>', 'noremap'),
        ('P', '<denite:change_path>', 'noremap'),
        ('b', '<denite:move_caret_to_one_word_left>', 'noremap'),
        ('w', '<denite:move_caret_to_next_word>', 'noremap'),
        ('e', '<denite:move_caret_to_end_of_word>', 'noremap'),
        ('0', '<denite:move_caret_to_head>', 'noremap'),
        ('$', '<denite:move_caret_to_tail>', 'noremap'),
        ('cc', '<denite:change_line>', 'noremap'),
        ('cw', '<denite:change_word>', 'noremap'),
        ('dd', '<denite:delete_entire_text>', 'noremap'),
        ('h', '<denite:move_caret_to_left>', 'noremap'),
        ('l', '<denite:move_caret_to_right>', 'noremap'),
        ('a', '<denite:append>', 'noremap'),
        ('A', '<denite:append_to_line>', 'noremap'),
        ('I', '<denite:insert_to_head>', 'noremap'),

        # Denite specific actions
        ('p', '<denite:do_action:preview>', 'noremap'),
        ('d', '<denite:do_action:delete>', 'noremap'),
        ('n', '<denite:do_action:new>', 'noremap'),
        ('t', '<denite:do_action:tabopen>', 'noremap'),
    ],
}
