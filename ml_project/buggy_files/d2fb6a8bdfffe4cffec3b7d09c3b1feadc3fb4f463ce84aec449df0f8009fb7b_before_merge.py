    def apply_transforms(self):
        # type: () -> None
        if isinstance(self.document, nodes.document):
            if hasattr(self.document.settings, 'env') and self.env:
                self.document.settings.env = self.env

            Transformer.apply_transforms(self)
        else:
            # wrap the target node by document node during transforming
            try:
                document = new_document('')
                if self.env:
                    document.settings.env = self.env
                document += self.document
                self.document = document
                Transformer.apply_transforms(self)
            finally:
                self.document = self.document[0]