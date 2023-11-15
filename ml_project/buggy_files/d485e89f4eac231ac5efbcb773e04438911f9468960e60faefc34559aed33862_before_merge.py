    def term(self, name):
        try:
            i = int(name)
            return URIRef("%s_%s" % (self.uri, i))
        except ValueError:
            return super(_RDFNamespace, self).term(name)