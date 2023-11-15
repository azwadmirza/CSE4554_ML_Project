    def setup_editor(self,
                     linenumbers=True,
                     language=None,
                     markers=False,
                     font=None,
                     color_scheme=None,
                     wrap=False,
                     tab_mode=True,
                     intelligent_backspace=True,
                     highlight_current_line=True,
                     highlight_current_cell=True,
                     occurrence_highlighting=True,
                     scrollflagarea=True,
                     edge_line=True,
                     edge_line_columns=(79,),
                     show_blanks=False,
                     close_parentheses=True,
                     close_quotes=False,
                     add_colons=True,
                     auto_unindent=True,
                     indent_chars=" "*4,
                     tab_stop_width_spaces=4,
                     cloned_from=None,
                     filename=None,
                     occurrence_timeout=1500,
                     show_class_func_dropdown=False,
                     indent_guides=False,
                     scroll_past_end=False):

        self.set_close_parentheses_enabled(close_parentheses)
        self.set_close_quotes_enabled(close_quotes)
        self.set_add_colons_enabled(add_colons)
        self.set_auto_unindent_enabled(auto_unindent)
        self.set_indent_chars(indent_chars)

        # Scrollbar flag area
        self.scrollflagarea.set_enabled(scrollflagarea)

        # Debugging
        self.debugger.set_filename(filename)

        # Edge line
        self.edge_line.set_enabled(edge_line)
        self.edge_line.set_columns(edge_line_columns)

        # Indent guides
        self.indent_guides.set_enabled(indent_guides)
        if self.indent_chars == '\t':
            self.indent_guides.set_indentation_width(self.tab_stop_width_spaces)
        else:
            self.indent_guides.set_indentation_width(len(self.indent_chars))

        # Blanks
        self.set_blanks_enabled(show_blanks)

        # Scrolling past the end
        self.set_scrollpastend_enabled(scroll_past_end)

        # Line number area
        if cloned_from:
            self.setFont(font) # this is required for line numbers area
        self.toggle_line_numbers(linenumbers, markers)

        # Lexer
        self.filename = filename
        self.set_language(language, filename)

        # Highlight current cell
        self.set_highlight_current_cell(highlight_current_cell)

        # Highlight current line
        self.set_highlight_current_line(highlight_current_line)

        # Occurrence highlighting
        self.set_occurrence_highlighting(occurrence_highlighting)
        self.set_occurrence_timeout(occurrence_timeout)

        # Tab always indents (even when cursor is not at the begin of line)
        self.set_tab_mode(tab_mode)

        # Intelligent backspace
        self.toggle_intelligent_backspace(intelligent_backspace)

        if cloned_from is not None:
            self.set_as_clone(cloned_from)
            self.panels.refresh()
        elif font is not None:
            self.set_font(font, color_scheme)
        elif color_scheme is not None:
            self.set_color_scheme(color_scheme)

        # Set tab spacing after font is set
        self.set_tab_stop_width_spaces(tab_stop_width_spaces)

        self.toggle_wrap_mode(wrap)

        # Class/Function dropdown will be disabled if we're not in a Python file.
        self.classfuncdropdown.setVisible(show_class_func_dropdown
                                          and self.is_python_like())