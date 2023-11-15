def create_key_bindings(history, python_input, history_mapping):
    """
    Key bindings.
    """
    bindings = KeyBindings()
    handle = bindings.add

    @handle(' ', filter=has_focus(history.history_buffer))
    def _(event):
        """
        Space: select/deselect line from history pane.
        """
        b = event.current_buffer
        line_no = b.document.cursor_position_row

        if not history_mapping.history_lines:
            # If we've no history, then nothing to do
            return

        if line_no in history_mapping.selected_lines:
            # Remove line.
            history_mapping.selected_lines.remove(line_no)
            history_mapping.update_default_buffer()
        else:
            # Add line.
            history_mapping.selected_lines.add(line_no)
            history_mapping.update_default_buffer()

            # Update cursor position
            default_buffer = history.default_buffer
            default_lineno = sorted(history_mapping.selected_lines).index(line_no) + \
                history_mapping.result_line_offset
            default_buffer.cursor_position = \
                default_buffer.document.translate_row_col_to_index(default_lineno, 0)

        # Also move the cursor to the next line. (This way they can hold
        # space to select a region.)
        b.cursor_position = b.document.translate_row_col_to_index(line_no + 1, 0)

    @handle(' ', filter=has_focus(DEFAULT_BUFFER))
    @handle('delete', filter=has_focus(DEFAULT_BUFFER))
    @handle('c-h', filter=has_focus(DEFAULT_BUFFER))
    def _(event):
        """
        Space: remove line from default pane.
        """
        b = event.current_buffer
        line_no = b.document.cursor_position_row - history_mapping.result_line_offset

        if line_no >= 0:
            try:
                history_lineno = sorted(history_mapping.selected_lines)[line_no]
            except IndexError:
                pass  # When `selected_lines` is an empty set.
            else:
                history_mapping.selected_lines.remove(history_lineno)

            history_mapping.update_default_buffer()

    help_focussed = has_focus(history.help_buffer)
    main_buffer_focussed = has_focus(history.history_buffer) | has_focus(history.default_buffer)

    @handle('tab', filter=main_buffer_focussed)
    @handle('c-x', filter=main_buffer_focussed, eager=True)
        # Eager: ignore the Emacs [Ctrl-X Ctrl-X] binding.
    @handle('c-w', filter=main_buffer_focussed)
    def _(event):
        " Select other window. "
        _select_other_window(history)

    @handle('f4')
    def _(event):
        " Switch between Emacs/Vi mode. "
        python_input.vi_mode = not python_input.vi_mode

    @handle('f1')
    def _(event):
        " Display/hide help. "
        _toggle_help(history)

    @handle('enter', filter=help_focussed)
    @handle('c-c', filter=help_focussed)
    @handle('c-g', filter=help_focussed)
    @handle('escape', filter=help_focussed)
    def _(event):
        " Leave help. "
        event.app.layout.focus_previous()

    @handle('q', filter=main_buffer_focussed)
    @handle('f3', filter=main_buffer_focussed)
    @handle('c-c', filter=main_buffer_focussed)
    @handle('c-g', filter=main_buffer_focussed)
    def _(event):
        " Cancel and go back. "
        event.app.exit(result=None)

    @handle('enter', filter=main_buffer_focussed)
    def _(event):
        " Accept input. "
        event.app.exit(result=history.default_buffer.text)

    enable_system_bindings = Condition(lambda: python_input.enable_system_bindings)

    @handle('c-z', filter=enable_system_bindings)
    def _(event):
        " Suspend to background. "
        event.app.suspend_to_background()

    return bindings