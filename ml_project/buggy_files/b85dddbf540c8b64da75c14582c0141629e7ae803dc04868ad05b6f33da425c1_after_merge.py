    def clear_doc(self, docname):
        # type: (unicode) -> None
        for key, (fn, _l) in list(self.data['progoptions'].items()):
            if fn == docname:
                del self.data['progoptions'][key]
        for key, (fn, _l) in list(self.data['objects'].items()):
            if fn == docname:
                del self.data['objects'][key]
        for key, (fn, _l, lineno) in list(self.data['citations'].items()):
            if fn == docname:
                del self.data['citations'][key]
        for key, docnames in list(self.data['citation_refs'].items()):
            if docnames == [docname]:
                del self.data['citation_refs'][key]
            elif docname in docnames:
                docnames.remove(docname)
        for key, (fn, _l, _l) in list(self.data['labels'].items()):
            if fn == docname:
                del self.data['labels'][key]
        for key, (fn, _l) in list(self.data['anonlabels'].items()):
            if fn == docname:
                del self.data['anonlabels'][key]