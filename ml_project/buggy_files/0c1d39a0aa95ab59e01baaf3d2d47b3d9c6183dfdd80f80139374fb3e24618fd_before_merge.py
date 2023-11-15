    def extendMarkdown(self, md):
        """ Insert AbbrPreprocessor before ReferencePreprocessor. """
        md.preprocessors.register(AbbrPreprocessor(md), 'abbr', 12)