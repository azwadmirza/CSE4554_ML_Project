    def register_editorstack(self, editorstack):
        self.editorstacks.append(editorstack)
        self.register_widget_shortcuts(editorstack)
        if len(self.editorstacks) > 1 and self.main is not None:
            # The first editostack is registered automatically with Spyder's
            # main window through the `register_plugin` method. Only additional
            # editors added by splitting need to be registered.
            # See Issue #5057.
            self.main.fileswitcher.sig_goto_file.connect(
                      editorstack.set_stack_index)

        if self.isAncestorOf(editorstack):
            # editorstack is a child of the Editor plugin
            self.set_last_focus_editorstack(self, editorstack)
            editorstack.set_closable( len(self.editorstacks) > 1 )
            if self.outlineexplorer is not None:
                editorstack.set_outlineexplorer(self.outlineexplorer.explorer)
            editorstack.set_find_widget(self.find_widget)
            editorstack.reset_statusbar.connect(self.readwrite_status.hide)
            editorstack.reset_statusbar.connect(self.encoding_status.hide)
            editorstack.reset_statusbar.connect(self.cursorpos_status.hide)
            editorstack.readonly_changed.connect(
                                        self.readwrite_status.update_readonly)
            editorstack.encoding_changed.connect(
                                         self.encoding_status.update_encoding)
            editorstack.sig_editor_cursor_position_changed.connect(
                                 self.cursorpos_status.update_cursor_position)
            editorstack.sig_refresh_eol_chars.connect(
                self.eol_status.update_eol)
            editorstack.current_file_changed.connect(
                self.vcs_status.update_vcs)
            editorstack.file_saved.connect(
                self.vcs_status.update_vcs_state)

        editorstack.autosave_mapping \
            = CONF.get('editor', 'autosave_mapping', {})
        editorstack.set_help(self.help)
        editorstack.set_io_actions(self.new_action, self.open_action,
                                   self.save_action, self.revert_action)
        editorstack.set_tempfile_path(self.TEMPFILE_PATH)

        settings = (
            ('set_pyflakes_enabled',                'code_analysis/pyflakes'),
            ('set_pep8_enabled',                    'code_analysis/pep8'),
            ('set_todolist_enabled',                'todo_list'),
            ('set_realtime_analysis_enabled',       'realtime_analysis'),
            ('set_realtime_analysis_timeout',       'realtime_analysis/timeout'),
            ('set_blanks_enabled',                  'blank_spaces'),
            ('set_scrollpastend_enabled',           'scroll_past_end'),
            ('set_linenumbers_enabled',             'line_numbers'),
            ('set_edgeline_enabled',                'edge_line'),
            ('set_edgeline_columns',                'edge_line_columns'),
            ('set_indent_guides',                   'indent_guides'),
            ('set_codecompletion_auto_enabled',     'codecompletion/auto'),
            ('set_codecompletion_case_enabled',     'codecompletion/case_sensitive'),
            ('set_codecompletion_enter_enabled',    'codecompletion/enter_key'),
            ('set_calltips_enabled',                'calltips'),
            ('set_go_to_definition_enabled',        'go_to_definition'),
            ('set_focus_to_editor',                 'focus_to_editor'),
            ('set_run_cell_copy',                   'run_cell_copy'),
            ('set_close_parentheses_enabled',       'close_parentheses'),
            ('set_close_quotes_enabled',            'close_quotes'),
            ('set_add_colons_enabled',              'add_colons'),
            ('set_auto_unindent_enabled',           'auto_unindent'),
            ('set_indent_chars',                    'indent_chars'),
            ('set_tab_stop_width_spaces',           'tab_stop_width_spaces'),
            ('set_wrap_enabled',                    'wrap'),
            ('set_tabmode_enabled',                 'tab_always_indent'),
            ('set_intelligent_backspace_enabled',   'intelligent_backspace'),
            ('set_highlight_current_line_enabled',  'highlight_current_line'),
            ('set_highlight_current_cell_enabled',  'highlight_current_cell'),
            ('set_occurrence_highlighting_enabled',  'occurrence_highlighting'),
            ('set_occurrence_highlighting_timeout',  'occurrence_highlighting/timeout'),
            ('set_checkeolchars_enabled',           'check_eol_chars'),
            ('set_tabbar_visible',                  'show_tab_bar'),
            ('set_classfunc_dropdown_visible',      'show_class_func_dropdown'),
            ('set_always_remove_trailing_spaces',   'always_remove_trailing_spaces'),
            ('set_convert_eol_on_save',             'convert_eol_on_save'),
            ('set_convert_eol_on_save_to',          'convert_eol_on_save_to'),
                    )
        for method, setting in settings:
            getattr(editorstack, method)(self.get_option(setting))
        editorstack.set_help_enabled(CONF.get('help', 'connect/editor'))
        color_scheme = self.get_color_scheme()
        editorstack.set_default_font(self.get_plugin_font(), color_scheme)

        editorstack.starting_long_process.connect(self.starting_long_process)
        editorstack.ending_long_process.connect(self.ending_long_process)

        # Redirect signals
        editorstack.sig_option_changed.connect(
                self.received_sig_option_changed)
        editorstack.redirect_stdio.connect(
                                 lambda state: self.redirect_stdio.emit(state))
        editorstack.exec_in_extconsole.connect(
                                    lambda text, option:
                                    self.exec_in_extconsole.emit(text, option))
        editorstack.run_cell_in_ipyclient.connect(
            lambda code, cell_name, filename, run_cell_copy:
            self.run_cell_in_ipyclient.emit(code, cell_name, filename,
                                            run_cell_copy))
        editorstack.update_plugin_title.connect(
                                   lambda: self.sig_update_plugin_title.emit())
        editorstack.editor_focus_changed.connect(self.save_focus_editorstack)
        editorstack.editor_focus_changed.connect(self.main.plugin_focus_changed)
        editorstack.zoom_in.connect(lambda: self.zoom(1))
        editorstack.zoom_out.connect(lambda: self.zoom(-1))
        editorstack.zoom_reset.connect(lambda: self.zoom(0))
        editorstack.sig_open_file.connect(self.report_open_file)
        editorstack.sig_new_file.connect(lambda s: self.new(text=s))
        editorstack.sig_new_file[()].connect(self.new)
        editorstack.sig_close_file.connect(self.close_file_in_all_editorstacks)
        editorstack.file_saved.connect(self.file_saved_in_editorstack)
        editorstack.file_renamed_in_data.connect(
                                      self.file_renamed_in_data_in_editorstack)
        editorstack.opened_files_list_changed.connect(
                                                self.opened_files_list_changed)
        editorstack.active_languages_stats.connect(
            self.update_active_languages)
        editorstack.sig_go_to_definition.connect(
            lambda fname, line, col: self.load(
                fname, line, start_column=col))
        editorstack.perform_lsp_request.connect(self.send_lsp_request)
        editorstack.todo_results_changed.connect(self.todo_results_changed)
        editorstack.update_code_analysis_actions.connect(
                                             self.update_code_analysis_actions)
        editorstack.update_code_analysis_actions.connect(
                                                      self.update_todo_actions)
        editorstack.refresh_file_dependent_actions.connect(
                                           self.refresh_file_dependent_actions)
        editorstack.refresh_save_all_action.connect(self.refresh_save_all_action)
        editorstack.sig_refresh_eol_chars.connect(self.refresh_eol_chars)
        editorstack.sig_breakpoints_saved.connect(self.breakpoints_saved)
        editorstack.text_changed_at.connect(self.text_changed_at)
        editorstack.current_file_changed.connect(self.current_file_changed)
        editorstack.plugin_load.connect(self.load)
        editorstack.plugin_load[()].connect(self.load)
        editorstack.edit_goto.connect(self.load)
        editorstack.sig_save_as.connect(self.save_as)
        editorstack.sig_prev_edit_pos.connect(self.go_to_last_edit_location)
        editorstack.sig_prev_cursor.connect(self.go_to_previous_cursor_position)
        editorstack.sig_next_cursor.connect(self.go_to_next_cursor_position)
        editorstack.sig_prev_warning.connect(self.go_to_previous_warning)
        editorstack.sig_next_warning.connect(self.go_to_next_warning)
        editorstack.sig_save_bookmark.connect(self.save_bookmark)
        editorstack.sig_load_bookmark.connect(self.load_bookmark)
        editorstack.sig_save_bookmarks.connect(self.save_bookmarks)