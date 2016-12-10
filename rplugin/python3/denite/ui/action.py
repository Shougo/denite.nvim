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


def _toggle_select_down(prompt, params):
    prompt.denite.toggle_select_cursor_candidate()
    return prompt.denite.move_to_next_line()


def _toggle_select_up(prompt, params):
    prompt.denite.toggle_select_cursor_candidate()
    return prompt.denite.move_to_prev_line()


DEFAULT_ACTION_RULES = [
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
    ('denite:toggle_select_down', _toggle_select_down),
    ('denite:toggle_select_up', _toggle_select_up),
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
        # Denite specific actions
        ('p', '<denite:do_action:preview>', 'noremap'),
        ('d', '<denite:do_action:delete>', 'noremap'),
        ('n', '<denite:do_action:new>', 'noremap'),
        ('t', '<denite:do_action:tabopen>', 'noremap'),
        ('q', '<denite:quit>', 'noremap'),
        ('<C-L>', '<denite:redraw>', 'noremap'),
        ('<C-R>', '<denite:restart>', 'noremap'),
        ('<Space>', '<denite:toggle_select_down>', 'noremap'),
    ],
}
