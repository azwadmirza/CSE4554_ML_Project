    def process_diagnostics(self, params):
        """Handle linting response."""
        try:
            self.process_code_analysis(params['params'])
        except RuntimeError:
            # This is triggered when a codeeditor instance has been
            # removed before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing linting")