    def handle_folding_range(self, response):
        """Handle folding response."""
        try:
            ranges = response['params']
            folding_panel = self.panels.get(FoldingPanel)

            # Update folding
            text = self.toPlainText()
            self.text_diff = (self.differ.diff_main(self.previous_text, text),
                              self.previous_text)
            folding_panel.update_folding(ranges)

            # Update indent guides, which depend on folding
            if self.indent_guides._enabled and len(self.patch) > 0:
                line, column = self.get_cursor_line_column()
                self.update_whitespace_count(line, column)
        except RuntimeError:
            # This is triggered when a codeeditor instance was removed
            # before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing folding")