    def process_diagnostics(self, params):
        """Handle linting response."""
        try:
            # The LSP spec doesn't require that folding be treated
            # in the same way as linting, i.e. to be recomputed on
            # didChange, didOpen and didSave. However, we think
            # that's necessary to maintain accurate folding all the
            # time. Therefore, we decided to add this request here.
            self.request_folding()

            self.process_code_analysis(params['params'])
        except RuntimeError:
            # This is triggered when a codeeditor instance was removed
            # before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing linting")