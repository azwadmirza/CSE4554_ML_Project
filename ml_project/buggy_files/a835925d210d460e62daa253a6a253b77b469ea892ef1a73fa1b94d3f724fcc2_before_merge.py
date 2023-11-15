    def apply(self):
        for node in self.document.footnotes:
            if node['names'][0] not in self.document.footnote_refs:
                logger.warning('Footnote [%s] is not referenced.', node['names'][0],
                               type='ref', subtype='footnote',
                               location=node)

        for node in self.document.autofootnotes:
            if not any(ref['auto'] == node['auto'] for ref in self.document.autofootnote_refs):
                logger.warning('Footnote [#] is not referenced.',
                               type='ref', subtype='footnote',
                               location=node)