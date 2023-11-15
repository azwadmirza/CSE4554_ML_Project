    def handle_go_to_definition(self, position):
        """Handle go to definition response."""
        try:
            position = position['params']
            if position is not None:
                def_range = position['range']
                start = def_range['start']
                if self.filename == position['file']:
                    self.go_to_line(start['line'] + 1,
                                    start['character'],
                                    None,
                                    word=None)
                else:
                    self.go_to_definition.emit(position['file'],
                                               start['line'] + 1,
                                               start['character'])
        except RuntimeError:
            # This is triggered when a codeeditor instance was removed
            # before the response can be processed.
            return
        except Exception:
            self.log_lsp_handle_errors(
                "Error when processing go to definition")