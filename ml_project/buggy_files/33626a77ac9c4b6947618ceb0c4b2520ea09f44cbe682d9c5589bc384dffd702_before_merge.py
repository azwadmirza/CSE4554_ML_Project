    def start_completion_services(self):
        logger.debug("Completions services available for: {0}".format(
            self.filename))
        self.completions_available = True
        self.document_did_open()