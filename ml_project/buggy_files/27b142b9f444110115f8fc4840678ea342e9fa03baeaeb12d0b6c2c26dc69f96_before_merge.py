    def find(self, changed=True, forward=True,
             rehighlight=True, start_highlight_timer=False):
        """Call the find function"""
        text = self.search_text.currentText()
        if len(text) == 0:
            self.search_text.lineEdit().setStyleSheet("")
            return None
        else:
            case = self.case_button.isChecked()
            words = self.words_button.isChecked()
            regexp = self.re_button.isChecked()
            found = self.editor.find_text(text, changed, forward, case=case,
                                          words=words, regexp=regexp)
            self.search_text.lineEdit().setStyleSheet(self.STYLE[found])
            if self.is_code_editor and found:
                if rehighlight or not self.editor.found_results:
                    self.highlight_timer.stop()
                    if start_highlight_timer:
                        self.highlight_timer.start()
                    else:
                        self.highlight_matches()
            else:
                self.clear_matches()
            return found