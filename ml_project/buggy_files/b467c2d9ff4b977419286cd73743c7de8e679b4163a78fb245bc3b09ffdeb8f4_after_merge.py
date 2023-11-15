    def keyPressEvent(self, event):
        """Reimplement Qt method."""
        if self.automatic_completions_after_ms > 0:
            self._timer_key_press.start(self.automatic_completions_after_ms)

        def insert_text(event):
            TextEditBaseWidget.keyPressEvent(self, event)
            self.document_did_change()
            self.sig_text_was_inserted.emit()

        # Send the signal to the editor's extension.
        event.ignore()
        self.sig_key_pressed.emit(event)

        key = event.key()
        text = to_text_string(event.text())
        has_selection = self.has_selected_text()
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier

        if text:
            self.__clear_occurrences()
        if QToolTip.isVisible():
            self.hide_tooltip_if_necessary(key)

        if event.isAccepted():
            # The event was handled by one of the editor extension.
            return

        if key in [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt,
                   Qt.Key_Meta, Qt.KeypadModifier]:
            # The user pressed only a modifier key.
            if ctrl:
                pos = self.mapFromGlobal(QCursor.pos())
                pos = self.calculate_real_position_from_global(pos)
                if self._handle_goto_uri_event(pos):
                    event.accept()
                    return

                if self._handle_goto_definition_event(pos):
                    event.accept()
                    return
            return

        # ---- Handle hard coded and builtin actions
        operators = {'+', '-', '*', '**', '/', '//', '%', '@', '<<', '>>',
                     '&', '|', '^', '~', '<', '>', '<=', '>=', '==', '!='}
        delimiters = {',', ':', ';', '@', '=', '->', '+=', '-=', '*=', '/=',
                      '//=', '%=', '@=', '&=', '|=', '^=', '>>=', '<<=', '**='}

        if not shift and not ctrl:
            self.hide_tooltip()

        if text not in self.auto_completion_characters:
            if text in operators or text in delimiters:
                self.completion_widget.hide()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            if not shift and not ctrl:
                if self.add_colons_enabled and self.is_python_like() and \
                  self.autoinsert_colons():
                    self.textCursor().beginEditBlock()
                    self.insert_text(':' + self.get_line_separator())
                    if self.strip_trailing_spaces_on_modify:
                        self.fix_and_strip_indent()
                    else:
                        self.fix_indent()
                    self.textCursor().endEditBlock()
                elif self.is_completion_widget_visible():
                    self.select_completion_list()
                else:
                    # Check if we're in a comment or a string at the
                    # current position
                    cmt_or_str_cursor = self.in_comment_or_string()

                    # Check if the line start with a comment or string
                    cursor = self.textCursor()
                    cursor.setPosition(cursor.block().position(),
                                       QTextCursor.KeepAnchor)
                    cmt_or_str_line_begin = self.in_comment_or_string(
                                                cursor=cursor)

                    # Check if we are in a comment or a string
                    cmt_or_str = cmt_or_str_cursor and cmt_or_str_line_begin

                    self.textCursor().beginEditBlock()
                    insert_text(event)
                    if self.strip_trailing_spaces_on_modify:
                        self.fix_and_strip_indent(
                            comment_or_string=cmt_or_str)
                    else:
                        self.fix_indent(comment_or_string=cmt_or_str)
                    self.textCursor().endEditBlock()
        elif key == Qt.Key_Insert and not shift and not ctrl:
            self.setOverwriteMode(not self.overwriteMode())
        elif key == Qt.Key_Backspace and not shift and not ctrl:
            leading_text = self.get_text('sol', 'cursor')
            leading_length = len(leading_text)
            trailing_spaces = leading_length-len(leading_text.rstrip())
            if has_selection or not self.intelligent_backspace:
                insert_text(event)
            else:
                trailing_text = self.get_text('cursor', 'eol')
                if not leading_text.strip() \
                   and leading_length > len(self.indent_chars):
                    if leading_length % len(self.indent_chars) == 0:
                        self.unindent()
                    else:
                        insert_text(event)
                elif trailing_spaces and not trailing_text.strip():
                    self.remove_suffix(leading_text[-trailing_spaces:])
                elif leading_text and trailing_text and \
                     leading_text[-1]+trailing_text[0] in ('()', '[]', '{}',
                                                           '\'\'', '""'):
                    cursor = self.textCursor()
                    cursor.movePosition(QTextCursor.PreviousCharacter)
                    cursor.movePosition(QTextCursor.NextCharacter,
                                        QTextCursor.KeepAnchor, 2)
                    cursor.removeSelectedText()
                else:
                    insert_text(event)
        elif key == Qt.Key_Home:
            self.stdkey_home(shift, ctrl)
        elif key == Qt.Key_End:
            # See spyder-ide/spyder#495: on MacOS X, it is necessary to
            # redefine this basic action which should have been implemented
            # natively
            self.stdkey_end(shift, ctrl)
        elif text in self.auto_completion_characters:
            self.insert_text(text)
            if text == ".":
                if not self.in_comment_or_string():
                    last_obj = getobj(self.get_text('sol', 'cursor'))
                    if last_obj and not last_obj.isdigit():
                        self.do_completion(automatic=True)
            else:
                self.do_completion(automatic=True)
        elif (text != '(' and text in self.signature_completion_characters and
                not self.has_selected_text()):
            self.insert_text(text)
            self.request_signature()
        elif key == Qt.Key_Colon and not has_selection \
             and self.auto_unindent_enabled:
            leading_text = self.get_text('sol', 'cursor')
            if leading_text.lstrip() in ('else', 'finally'):
                ind = lambda txt: len(txt)-len(txt.lstrip())
                prevtxt = to_text_string(self.textCursor(
                                                ).block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            insert_text(event)
        elif key == Qt.Key_Space and not shift and not ctrl \
             and not has_selection and self.auto_unindent_enabled:
            self.completion_widget.hide()
            leading_text = self.get_text('sol', 'cursor')
            if leading_text.lstrip() in ('elif', 'except'):
                ind = lambda txt: len(txt)-len(txt.lstrip())
                prevtxt = to_text_string(self.textCursor(
                                                ).block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            insert_text(event)
        elif key == Qt.Key_Tab and not ctrl:
            # Important note: <TAB> can't be called with a QShortcut because
            # of its singular role with respect to widget focus management
            if not has_selection and not self.tab_mode:
                self.intelligent_tab()
            else:
                # indent the selected text
                self.indent_or_replace()
        elif key == Qt.Key_Backtab and not ctrl:
            # Backtab, i.e. Shift+<TAB>, could be treated as a QShortcut but
            # there is no point since <TAB> can't (see above)
            if not has_selection and not self.tab_mode:
                self.intelligent_backtab()
            else:
                # indent the selected text
                self.unindent()
            event.accept()
        elif not event.isAccepted():
            insert_text(event)

        self._last_key_pressed_text = text
        if self.automatic_completions_after_ms == 0:
            self._handle_completions()

        if not event.modifiers():
            # Accept event to avoid it being handled by the parent
            # Modifiers should be passed to the parent because they
            # could be shortcuts
            event.accept()