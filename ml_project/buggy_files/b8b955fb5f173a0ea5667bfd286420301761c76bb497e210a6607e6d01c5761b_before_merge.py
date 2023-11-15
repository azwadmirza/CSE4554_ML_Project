    def apply_post_transforms(self, doctree, docname):
        # type: (nodes.Node, unicode) -> None
        """Apply all post-transforms."""
        try:
            # set env.docname during applying post-transforms
            self.temp_data['docname'] = docname
            if hasattr(doctree, 'settings'):
                doctree.settings.env = self

            transformer = SphinxTransformer(doctree)
            transformer.add_transforms(self.app.post_transforms)
            transformer.apply_transforms()
        finally:
            self.temp_data.clear()

        # allow custom references to be resolved
        self.app.emit('doctree-resolved', doctree, docname)