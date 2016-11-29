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


def _move_to_prev_line(prompt, params):
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


def _jump_to_prev_source(prompt, params):
    return prompt.denite.jump_to_prev_source()


def _input_command_line(prompt, params):
    from ..prompt.util import ESCAPE_ECHO
    prompt.nvim.command('redraw | echo')
    text = prompt.nvim.call('input', prompt.prefix)
    prompt.update_text(text)


def _enter_mode(prompt, params):
    return prompt.denite.enter_mode(params)


def _leave_mode(prompt, params):
    return prompt.denite.leave_mode()


def _suspend(prompt, params):
    return prompt.denite.suspend()


DEFAULT_ACTION_RULES = [
    ('denite:redraw', _redraw),
    ('denite:quit', _quit),
    ('denite:do_action', _do_action),
    ('denite:choose_action', _choose_action),
    ('denite:move_to_next_line', _move_to_next_line),
    ('denite:move_to_prev_line', _move_to_prev_line),
    ('denite:move_to_first_line', _move_to_first_line),
    ('denite:move_to_last_line', _move_to_last_line),
    ('denite:scroll_window_upwards', _scroll_window_upwards),
    ('denite:scroll_window_downwards', _scroll_window_downwards),
    ('denite:scroll_page_forwards', _scroll_page_forwards),
    ('denite:scroll_page_backwards', _scroll_page_backwards),
    ('denite:scroll_up', _scroll_up),
    ('denite:scroll_down', _scroll_down),
    ('denite:jump_to_next_source', _jump_to_next_source),
    ('denite:jump_to_prev_source', _jump_to_prev_source),
    ('denite:input_command_line', _input_command_line),
    ('denite:enter_mode', _enter_mode),
    ('denite:leave_mode', _leave_mode),
    ('denite:suspend', _suspend),
]

DEFAULT_ACTION_KEYMAP = [
    ('<Esc>', '<denite:leave_mode>', 'noremap'),
    ('<CR>', '<denite:do_action:default>', 'noremap'),
    ('<C-M>', '<denite:do_action:default>', 'noremap'),
    ('<C-Z>', '<denite:suspend>', 'noremap'),
    ('<Tab>', '<denite:choose_action>', 'noremap'),
]

INSERT_ACTION_KEYMAP = [
    # Behave like Vim's builtin command-line
    ('<C-B>', '<prompt:move_caret_to_head>', 'noremap'),
    ('<C-E>', '<prompt:move_caret_to_tail>', 'noremap'),
    ('<BS>', '<prompt:delete_char_before_caret>', 'noremap'),
    ('<C-H>', '<prompt:delete_char_before_caret>', 'noremap'),
    ('<C-K>', '<prompt:insert_digraph>', 'noremap'),
    ('<C-N>', '<prompt:assign_next_text>', 'noremap'),
    ('<C-P>', '<prompt:assign_previous_text>', 'noremap'),
    ('<C-Q>', '<prompt:insert_special>', 'noremap'),
    ('<C-R>', '<prompt:paste_from_register>', 'noremap'),
    ('<C-U>', '<prompt:delete_entire_text>', 'noremap'),
    ('<C-V>', '<prompt:insert_special>', 'noremap'),
    ('<C-W>', '<prompt:delete_word_before_caret>', 'noremap'),
    ('<DEL>', '<prompt:delete_char_under_caret>', 'noremap'),
    ('<Left>', '<prompt:move_caret_to_left>', 'noremap'),
    ('<S-Left>', '<prompt:move_caret_to_one_word_left>', 'noremap'),
    ('<C-Left>', '<prompt:move_caret_to_one_word_left>', 'noremap'),
    ('<Right>', '<prompt:move_caret_to_right>', 'noremap'),
    ('<S-Right>', '<prompt:move_caret_to_one_word_right>', 'noremap'),
    ('<C-Right>', '<prompt:move_caret_to_one_word_right>', 'noremap'),
    ('<Up>', '<prompt:assign_previous_matched_text>', 'noremap'),
    ('<S-Up>', '<prompt:assign_previous_text>', 'noremap'),
    ('<Down>', '<prompt:assign_next_matched_text>', 'noremap'),
    ('<S-Down>', '<prompt:assign_next_text>', 'noremap'),
    ('<Home>', '<prompt:move_caret_to_head>', 'noremap'),
    ('<End>', '<prompt:move_caret_to_tail>', 'noremap'),
    ('<PageDown>', '<prompt:assign_next_text>', 'noremap'),
    ('<PageUp>', '<prompt:assign_previous_text>', 'noremap'),
    ('<INSERT>', '<prompt:toggle_insert_mode>', 'noremap'),
    # Denite specific actions
    ('<C-G>', '<denite:move_to_next_line>', 'noremap'),
    ('<Tab>', '<denite:move_to_next_line>', 'noremap'),
    ('<C-T>', '<denite:move_to_prev_line>', 'noremap'),
    ('<S-Tab>', '<denite:move_to_prev_line>', 'noremap'),
    ('<C-L>', '<denite:redraw>', 'noremap'),
    ('<C-O>', '<denite:enter_mode:normal>', 'noremap'),
    ('<C-J>', '<denite:input_command_line>', 'noremap'),
]

NORMAL_ACTION_KEYMAP = [
    ('i', '<denite:enter_mode:insert>', 'noremap'),
    ('j', '<denite:move_to_next_line>', 'noremap'),
    ('k', '<denite:move_to_prev_line>', 'noremap'),
    ('gg', '<denite:move_to_first_line>', 'noremap'),
    ('G', '<denite:move_to_last_line>', 'noremap'),
    ('<C-U>', '<denite:scroll_window_upwards>', 'noremap'),
    ('<C-D>', '<denite:scroll_window_downwards>', 'noremap'),
    ('<C-F>', '<denite:scroll_page_forwards>', 'noremap'),
    ('<C-B>', '<denite:scroll_page_backwards>', 'noremap'),
    ('p', '<denite:do_action:preview>', 'noremap'),
    ('d', '<denite:do_action:delete>', 'noremap'),
    ('n', '<denite:do_action:new>', 'noremap'),
    ('t', '<denite:do_action:tabopen>', 'noremap'),
    ('q', '<denite:quit>', 'noremap'),
]
