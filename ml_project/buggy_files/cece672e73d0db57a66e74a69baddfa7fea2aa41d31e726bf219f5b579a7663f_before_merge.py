    def update_completion_configuration(self, config):
        """Start LSP integration if it wasn't done before."""
        logger.debug("LSP available for: %s" % self.filename)
        self.parse_lsp_config(config)
        self.completions_available = True
        self.document_did_open()
        self.request_folding()