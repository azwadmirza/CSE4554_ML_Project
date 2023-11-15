    def keyPressEvent(self, event):
        """Reimplement Qt method"""
        # Send the signal to the editor's extension.
        event.ignore()
        self.sig_key_pressed.emit(event)

        key = event.key()
        text = to_text_string(event.text())
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
            return

        # ---- Handle hard coded and builtin actions
        has_selection = self.has_selected_text()
        ctrl = event.modifiers() & Qt.ControlModifier
        shift = event.modifiers() & Qt.ShiftModifier
        if key in (Qt.Key_Enter, Qt.Key_Return):
            if not shift and not ctrl:
                if self.add_colons_enabled and self.is_python_like() and \
                  self.autoinsert_colons():
                    self.textCursor().beginEditBlock()
                    self.insert_text(':' + self.get_line_separator())
                    self.fix_indent()
                    self.textCursor().endEditBlock()
                elif self.is_completion_widget_visible() \
                   and self.codecompletion_enter:
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
                    TextEditBaseWidget.keyPressEvent(self, event)
                    self.fix_indent(comment_or_string=cmt_or_str)
                    self.textCursor().endEditBlock()
        elif key == Qt.Key_Insert and not shift and not ctrl:
            self.setOverwriteMode(not self.overwriteMode())
        elif key == Qt.Key_Backspace and not shift and not ctrl:
            leading_text = self.get_text('sol', 'cursor')
            leading_length = len(leading_text)
            trailing_spaces = leading_length-len(leading_text.rstrip())
            if has_selection or not self.intelligent_backspace:
                TextEditBaseWidget.keyPressEvent(self, event)
            else:
                trailing_text = self.get_text('cursor', 'eol')
                if not leading_text.strip() \
                   and leading_length > len(self.indent_chars):
                    if leading_length % len(self.indent_chars) == 0:
                        self.unindent()
                    else:
                        TextEditBaseWidget.keyPressEvent(self, event)
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
                    TextEditBaseWidget.keyPressEvent(self, event)
                    if self.is_completion_widget_visible():
                        self.completion_text = self.completion_text[:-1]
        # elif key == Qt.Key_Period:
        #     self.insert_text(text)
        #     if (self.is_python_like()) and not \
        #       self.in_comment_or_string() and self.codecompletion_auto:
        #         # Enable auto-completion only if last token isn't a float
        #         last_obj = getobj(self.get_text('sol', 'cursor'))
        #         if last_obj and not last_obj.isdigit():
        #             self.do_completion(automatic=True)
        elif key == Qt.Key_Home:
            self.stdkey_home(shift, ctrl)
        elif key == Qt.Key_End:
            # See Issue 495: on MacOS X, it is necessary to redefine this
            # basic action which should have been implemented natively
            self.stdkey_end(shift, ctrl)
        elif text in self.auto_completion_characters:
            self.insert_text(text)
            if not self.in_comment_or_string() and self.codecompletion_auto:
                last_obj = getobj(self.get_text('sol', 'cursor'))
                if last_obj and not last_obj.isdigit():
                    self.do_completion(automatic=True)
        elif (text != '(' and text in self.signature_completion_characters and
                not self.has_selected_text()):
            self.insert_text(text)
            self.request_signature()
        elif (text == '(' and
              not self.has_selected_text()):
            # self.hide_completion_widget()
            self.handle_parentheses(text)
        elif (text in ('[', '{') and not has_selection and
              self.close_parentheses_enabled):
            s_trailing_text = self.get_text('cursor', 'eol').strip()
            if len(s_trailing_text) == 0 or \
               s_trailing_text[0] in (',', ')', ']', '}'):
                self.insert_text({'{': '{}', '[': '[]'}[text])
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.PreviousCharacter)
                self.setTextCursor(cursor)
            else:
                TextEditBaseWidget.keyPressEvent(self, event)
        elif key in (Qt.Key_ParenRight, Qt.Key_BraceRight, Qt.Key_BracketRight)\
          and not has_selection and self.close_parentheses_enabled \
          and not self.textCursor().atBlockEnd():
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)
            text = to_text_string(cursor.selectedText())
            key_matches_next_char = (
                text == {Qt.Key_ParenRight: ')', Qt.Key_BraceRight: '}',
                         Qt.Key_BracketRight: ']'}[key]
            )
            if (key_matches_next_char
                    and not self.__unmatched_braces_in_line(
                        cursor.block().text(), text)):
                # overwrite an existing brace if all braces in line are matched
                cursor.clearSelection()
                self.setTextCursor(cursor)
            else:
                TextEditBaseWidget.keyPressEvent(self, event)
        elif key == Qt.Key_Colon and not has_selection \
             and self.auto_unindent_enabled:
            leading_text = self.get_text('sol', 'cursor')
            if leading_text.lstrip() in ('else', 'finally'):
                ind = lambda txt: len(txt)-len(txt.lstrip())
                prevtxt = to_text_string(self.textCursor(
                                                ).block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            TextEditBaseWidget.keyPressEvent(self, event)
        elif key == Qt.Key_Space and not shift and not ctrl \
             and not has_selection and self.auto_unindent_enabled:
            leading_text = self.get_text('sol', 'cursor')
            if leading_text.lstrip() in ('elif', 'except'):
                ind = lambda txt: len(txt)-len(txt.lstrip())
                prevtxt = to_text_string(self.textCursor(
                                                ).block().previous().text())
                if ind(leading_text) == ind(prevtxt):
                    self.unindent(force=True)
            TextEditBaseWidget.keyPressEvent(self, event)
        elif key == Qt.Key_Tab:
            # Important note: <TAB> can't be called with a QShortcut because
            # of its singular role with respect to widget focus management
            if not has_selection and not self.tab_mode:
                self.intelligent_tab()
            else:
                # indent the selected text
                self.indent_or_replace()
        elif key == Qt.Key_Backtab:
            # Backtab, i.e. Shift+<TAB>, could be treated as a QShortcut but
            # there is no point since <TAB> can't (see above)
            if not has_selection and not self.tab_mode:
                self.intelligent_backtab()
            else:
                # indent the selected text
                self.unindent()
            event.accept()
        elif not event.isAccepted():
            TextEditBaseWidget.keyPressEvent(self, event)
            if self.is_completion_widget_visible() and text:
                self.completion_text += text
        if len(text) > 0:
            self.document_did_change(text)
            # self.do_completion(automatic=True)
        if not event.modifiers():
            # Accept event to avoid it being handled by the parent
            # Modifiers should be passed to the parent because they
            # could be shortcuts
            event.accept()