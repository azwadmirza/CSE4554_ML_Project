    def handle_hover_response(self, contents):
        """Handle hover response."""
        try:
            content = contents['params']
            self.sig_display_object_info.emit(content,
                                              self._request_hover_clicked)
            if self._show_hint and self._last_point and content:
                # This is located in spyder/widgets/mixins.py
                word = self._last_hover_word,
                content = content.replace(u'\xa0', ' ')
                self.show_hint(content, inspect_word=word,
                               at_point=self._last_point)
                self._last_point = None
        except RuntimeError:
            # This is triggered when a codeeditor instance has been
            # removed before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing hover")