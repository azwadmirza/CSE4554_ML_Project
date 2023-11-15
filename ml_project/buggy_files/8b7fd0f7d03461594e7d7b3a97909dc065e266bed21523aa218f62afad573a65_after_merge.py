    def process_signatures(self, params):
        """Handle signature response."""
        try:
            signature_params = params['params']

            if (signature_params is not None and
                    'activeParameter' in signature_params):
                self.sig_signature_invoked.emit(signature_params)
                signature_data = signature_params['signatures']
                documentation = signature_data['documentation']

                # The language server returns encoded text with
                # spaces defined as `\xa0`
                documentation = documentation.replace(u'\xa0', ' ')

                parameter_idx = signature_params['activeParameter']
                parameters = signature_data['parameters']
                parameter = None
                if len(parameters) > 0 and parameter_idx < len(parameters):
                    parameter_data = parameters[parameter_idx]
                    parameter = parameter_data['label']

                signature = signature_data['label']

                # This method is part of spyder/widgets/mixins
                self.show_calltip(
                    signature=signature,
                    parameter=parameter,
                    language=self.language,
                    documentation=documentation,
                )
        except RuntimeError:
            # This is triggered when a codeeditor instance was removed
            # before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors("Error when processing signature")