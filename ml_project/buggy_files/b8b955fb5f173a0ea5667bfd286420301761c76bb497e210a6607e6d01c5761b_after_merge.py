    def apply_post_transforms(self, doctree, docname):
        # type: (nodes.Node, unicode) -> None
        """Apply all post-transforms."""
        try:
            # set env.docname during applying post-transforms
            self.temp_data['docname'] = docname

            transformer = SphinxTransformer(doctree)
            transformer.set_environment(self)
            transformer.add_transforms(self.app.post_transforms)
            transformer.apply_transforms()
        finally:
            self.temp_data.clear()

        # allow custom references to be resolved
        self.app.emit('doctree-resolved', doctree, docname)