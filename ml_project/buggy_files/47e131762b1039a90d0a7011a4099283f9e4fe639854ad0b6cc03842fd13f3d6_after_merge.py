    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings"""
        if self.editorstacks is not None:
            # --- syntax highlight and text rendering settings
            color_scheme_n = 'color_scheme_name'
            color_scheme_o = self.get_color_scheme()
            currentline_n = 'highlight_current_line'
            currentline_o = self.get_option(currentline_n)
            currentcell_n = 'highlight_current_cell'
            currentcell_o = self.get_option(currentcell_n)
            occurrence_n = 'occurrence_highlighting'
            occurrence_o = self.get_option(occurrence_n)
            occurrence_timeout_n = 'occurrence_highlighting/timeout'
            occurrence_timeout_o = self.get_option(occurrence_timeout_n)
            focus_to_editor_n = 'focus_to_editor'
            focus_to_editor_o = self.get_option(focus_to_editor_n)

            for editorstack in self.editorstacks:
                if color_scheme_n in options:
                    editorstack.set_color_scheme(color_scheme_o)
                if currentline_n in options:
                    editorstack.set_highlight_current_line_enabled(
                                                                currentline_o)
                if currentcell_n in options:
                    editorstack.set_highlight_current_cell_enabled(
                                                                currentcell_o)
                if occurrence_n in options:
                    editorstack.set_occurrence_highlighting_enabled(occurrence_o)
                if occurrence_timeout_n in options:
                    editorstack.set_occurrence_highlighting_timeout(
                                                           occurrence_timeout_o)
                if focus_to_editor_n in options:
                    editorstack.set_focus_to_editor(focus_to_editor_o)

            # --- everything else
            tabbar_n = 'show_tab_bar'
            tabbar_o = self.get_option(tabbar_n)
            classfuncdropdown_n = 'show_class_func_dropdown'
            classfuncdropdown_o = self.get_option(classfuncdropdown_n)
            linenb_n = 'line_numbers'
            linenb_o = self.get_option(linenb_n)
            blanks_n = 'blank_spaces'
            blanks_o = self.get_option(blanks_n)
            scrollpastend_n = 'scroll_past_end'
            scrollpastend_o = self.get_option(scrollpastend_n)
            edgeline_n = 'edge_line'
            edgeline_o = self.get_option(edgeline_n)
            edgelinecols_n = 'edge_line_columns'
            edgelinecols_o = self.get_option(edgelinecols_n)
            wrap_n = 'wrap'
            wrap_o = self.get_option(wrap_n)
            indentguides_n = 'indent_guides'
            indentguides_o = self.get_option(indentguides_n)
            tabindent_n = 'tab_always_indent'
            tabindent_o = self.get_option(tabindent_n)
            ibackspace_n = 'intelligent_backspace'
            ibackspace_o = self.get_option(ibackspace_n)
            removetrail_n = 'always_remove_trailing_spaces'
            removetrail_o = self.get_option(removetrail_n)
            converteol_n = 'convert_eol_on_save'
            converteol_o = self.get_option(converteol_n)
            converteolto_n = 'convert_eol_on_save_to'
            converteolto_o = self.get_option(converteolto_n)
            runcellcopy_n = 'run_cell_copy'
            runcellcopy_o = self.get_option(runcellcopy_n)
            closepar_n = 'close_parentheses'
            closepar_o = self.get_option(closepar_n)
            close_quotes_n = 'close_quotes'
            close_quotes_o = self.get_option(close_quotes_n)
            add_colons_n = 'add_colons'
            add_colons_o = self.get_option(add_colons_n)
            autounindent_n = 'auto_unindent'
            autounindent_o = self.get_option(autounindent_n)
            indent_chars_n = 'indent_chars'
            indent_chars_o = self.get_option(indent_chars_n)
            tab_stop_width_spaces_n = 'tab_stop_width_spaces'
            tab_stop_width_spaces_o = self.get_option(tab_stop_width_spaces_n)
            help_n = 'connect_to_oi'
            help_o = CONF.get('help', 'connect/editor')
            todo_n = 'todo_list'
            todo_o = self.get_option(todo_n)

            finfo = self.get_current_finfo()


            for editorstack in self.editorstacks:
                if tabbar_n in options:
                    editorstack.set_tabbar_visible(tabbar_o)
                if linenb_n in options:
                    editorstack.set_linenumbers_enabled(linenb_o,
                                                        current_finfo=finfo)
                if edgeline_n in options:
                    editorstack.set_edgeline_enabled(edgeline_o)
                if edgelinecols_n in options:
                    editorstack.set_edgeline_columns(edgelinecols_o)
                if wrap_n in options:
                    editorstack.set_wrap_enabled(wrap_o)
                if tabindent_n in options:
                    editorstack.set_tabmode_enabled(tabindent_o)
                if ibackspace_n in options:
                    editorstack.set_intelligent_backspace_enabled(ibackspace_o)
                if removetrail_n in options:
                    editorstack.set_always_remove_trailing_spaces(removetrail_o)
                if converteol_n in options:
                    editorstack.set_convert_eol_on_save(converteol_o)
                if converteolto_n in options:
                    editorstack.set_convert_eol_on_save_to(converteolto_o)
                if runcellcopy_n in options:
                    editorstack.set_run_cell_copy(runcellcopy_o)
                if closepar_n in options:
                    editorstack.set_close_parentheses_enabled(closepar_o)
                if close_quotes_n in options:
                    editorstack.set_close_quotes_enabled(close_quotes_o)
                if add_colons_n in options:
                    editorstack.set_add_colons_enabled(add_colons_o)
                if autounindent_n in options:
                    editorstack.set_auto_unindent_enabled(autounindent_o)
                if indent_chars_n in options:
                    editorstack.set_indent_chars(indent_chars_o)
                if tab_stop_width_spaces_n in options:
                    editorstack.set_tab_stop_width_spaces(tab_stop_width_spaces_o)
                if help_n in options:
                    editorstack.set_help_enabled(help_o)
                if todo_n in options:
                    editorstack.set_todolist_enabled(todo_o,
                                                     current_finfo=finfo)

            for name, action in self.checkable_actions.items():
                if name in options:
                    state = self.get_option(name)
                    action.setChecked(state)
                    action.trigger()

            # Multiply by 1000 to convert seconds to milliseconds
            self.autosave.interval = (
                    self.get_option('autosave_interval') * 1000)
            self.autosave.enabled = self.get_option('autosave_enabled')

            # We must update the current editor after the others:
            # (otherwise, code analysis buttons state would correspond to the
            #  last editor instead of showing the one of the current editor)
            if finfo is not None:
                # TODO: Connect this to the LSP
                if todo_n in options and todo_o:
                    finfo.run_todo_finder()