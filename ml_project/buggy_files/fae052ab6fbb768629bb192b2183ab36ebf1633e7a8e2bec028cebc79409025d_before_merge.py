    def create_new_editor(self, fname, enc, txt, set_current, new=False,
                          cloned_from=None, add_where='end'):
        """
        Create a new editor instance
        Returns finfo object (instead of editor as in previous releases)
        """
        editor = codeeditor.CodeEditor(self)
        editor.go_to_definition.connect(
            lambda fname, line, column: self.sig_go_to_definition.emit(
                fname, line, column))

        finfo = FileInfo(fname, enc, editor, new, self.threadmanager)

        self.add_to_data(finfo, set_current, add_where)
        finfo.send_to_help.connect(self.send_to_help)
        finfo.sig_show_object_info.connect(self.inspect_current_object)
        finfo.todo_results_changed.connect(
            lambda: self.todo_results_changed.emit())
        finfo.edit_goto.connect(lambda fname, lineno, name:
                                self.edit_goto.emit(fname, lineno, name))
        finfo.sig_save_bookmarks.connect(lambda s1, s2:
                                         self.sig_save_bookmarks.emit(s1, s2))
        editor.sig_run_selection.connect(self.run_selection)
        editor.sig_run_cell.connect(self.run_cell)
        editor.sig_run_cell_and_advance.connect(self.run_cell_and_advance)
        editor.sig_re_run_last_cell.connect(self.re_run_last_cell)
        editor.sig_new_file.connect(self.sig_new_file.emit)
        editor.sig_breakpoints_saved.connect(self.sig_breakpoints_saved)
        editor.sig_process_code_analysis.connect(
            lambda: self.update_code_analysis_actions.emit())
        language = get_file_language(fname, txt)
        editor.setup_editor(
            linenumbers=self.linenumbers_enabled,
            show_blanks=self.blanks_enabled,
            underline_errors=self.underline_errors_enabled,
            scroll_past_end=self.scrollpastend_enabled,
            edge_line=self.edgeline_enabled,
            edge_line_columns=self.edgeline_columns, language=language,
            markers=self.has_markers(), font=self.default_font,
            color_scheme=self.color_scheme,
            wrap=self.wrap_enabled, tab_mode=self.tabmode_enabled,
            strip_mode=self.stripmode_enabled,
            intelligent_backspace=self.intelligent_backspace_enabled,
            automatic_completions=self.automatic_completions_enabled,
            highlight_current_line=self.highlight_current_line_enabled,
            highlight_current_cell=self.highlight_current_cell_enabled,
            occurrence_highlighting=self.occurrence_highlighting_enabled,
            occurrence_timeout=self.occurrence_highlighting_timeout,
            close_parentheses=self.close_parentheses_enabled,
            close_quotes=self.close_quotes_enabled,
            add_colons=self.add_colons_enabled,
            auto_unindent=self.auto_unindent_enabled,
            indent_chars=self.indent_chars,
            tab_stop_width_spaces=self.tab_stop_width_spaces,
            cloned_from=cloned_from,
            filename=fname,
            show_class_func_dropdown=self.show_class_func_dropdown,
            indent_guides=self.indent_guides,
        )
        if cloned_from is None:
            editor.set_text(txt)
            editor.document().setModified(False)
        finfo.text_changed_at.connect(
            lambda fname, position:
            self.text_changed_at.emit(fname, position))
        editor.sig_cursor_position_changed.connect(
                                           self.editor_cursor_position_changed)
        editor.textChanged.connect(self.start_stop_analysis_timer)

        def perform_completion_request(lang, method, params):
            self.sig_perform_completion_request.emit(lang, method, params)

        editor.sig_perform_completion_request.connect(
            perform_completion_request)
        editor.modificationChanged.connect(
            lambda state: self.modification_changed(state,
                editor_id=id(editor)))
        editor.focus_in.connect(self.focus_changed)
        editor.zoom_in.connect(lambda: self.zoom_in.emit())
        editor.zoom_out.connect(lambda: self.zoom_out.emit())
        editor.zoom_reset.connect(lambda: self.zoom_reset.emit())
        editor.sig_eol_chars_changed.connect(
            lambda eol_chars: self.refresh_eol_chars(eol_chars))

        self.find_widget.set_editor(editor)

        self.refresh_file_dependent_actions.emit()
        self.modification_changed(index=self.data.index(finfo))

        # Needs to reset the highlighting on startup in case the PygmentsSH
        # is in use
        editor.run_pygments_highlighter()
        options = {
            'language': editor.language,
            'filename': editor.filename,
            'codeeditor': editor
        }
        self.sig_open_file.emit(options)
        if self.get_stack_index() == 0:
            self.current_changed(0)

        return finfo