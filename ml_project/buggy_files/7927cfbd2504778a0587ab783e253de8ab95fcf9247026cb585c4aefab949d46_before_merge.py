    def absolutize(self, iri):

        """
        Apply BASE / PREFIXes to URIs
        (and to datatypes in Literals)

        TODO: Move resolving URIs to pre-processing
        """

        if isinstance(iri, CompValue):
            if iri.name == 'pname':
                return self.resolvePName(iri.prefix, iri.localname)
            if iri.name == 'literal':
                return Literal(
                    iri.string, lang=iri.lang,
                    datatype=self.absolutize(iri.datatype))
        elif isinstance(iri, URIRef) and not ':' in iri:  # TODO: Check for relative URI?
            return URIRef(self.base + iri)
        return iri