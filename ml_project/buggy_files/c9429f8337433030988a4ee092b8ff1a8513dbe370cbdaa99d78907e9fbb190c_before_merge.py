    def _index(self, id, body, **kwargs):
        return self.server.index(
            index=self.index,
            doc_type=self.doc_type,
            **kwargs
        )