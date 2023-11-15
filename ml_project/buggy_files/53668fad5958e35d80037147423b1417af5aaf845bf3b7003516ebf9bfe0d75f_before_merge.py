    def handle_hover_response(self, contents):
        """Handle hover response."""
        try:
            content = contents['params']
            self.sig_display_object_info.emit(content)

            if CONF.get('lsp-server', 'enable_hover_hints') and content:
                if self._show_hint and self._last_point:
                    # This is located in spyder/widgets/mixins.py
                    word = self._last_hover_word,
                    self.show_hint(content, inspect_word=word,
                                   at_point=self._last_point)
                    self._last_point = None

        except Exception:
            self.log_lsp_handle_errors("Error when processing hover")