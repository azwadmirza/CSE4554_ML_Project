    def title(self):
        # overrides unicode.title to allow DCTERMS.title for example
        return URIRef(self + 'title')