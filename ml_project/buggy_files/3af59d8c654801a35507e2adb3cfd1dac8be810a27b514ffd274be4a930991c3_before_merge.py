    def clear_doc(self, docname):
        # type: (unicode) -> None
        rootSymbol = self.data['root_symbol']
        rootSymbol.clear_doc(docname)
        for name, nDocname in list(self.data['names'].items()):
            if nDocname == docname:
                del self.data['names'][name]