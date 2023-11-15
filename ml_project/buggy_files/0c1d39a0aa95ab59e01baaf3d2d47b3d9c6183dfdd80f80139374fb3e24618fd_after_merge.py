    def extendMarkdown(self, md):
        """ Insert AbbrPreprocessor before ReferencePreprocessor. """
        md.parser.blockprocessors.register(AbbrPreprocessor(md.parser), 'abbr', 16)