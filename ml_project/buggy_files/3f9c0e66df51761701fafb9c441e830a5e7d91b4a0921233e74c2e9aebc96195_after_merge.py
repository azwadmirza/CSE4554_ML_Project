    def handle_hover_response(self, contents):
        """Handle hover response."""
        if running_under_pytest():
            try:
                from unittest.mock import Mock
            except ImportError:
                from mock import Mock  # Python 2

            # On some tests this is returning a Mock
            if isinstance(contents, Mock):
                return

        try:
            content = contents['params']

            if running_under_pytest():
                # On some tests this is returning a list
                if isinstance(content, list):
                    return

            self.sig_display_object_info.emit(content,
                                              self._request_hover_clicked)
            if content is not None and self._show_hint and self._last_point:
                # This is located in spyder/widgets/mixins.py
                word = self._last_hover_word
                content = content.replace(u'\xa0', ' ')
                self.show_hint(content, inspect_word=word,
                               at_point=self._last_point)
                self._last_point = None
        except RuntimeError:
            # This is triggered when a codeeditor instance was removed
            # before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing hover")