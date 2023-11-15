def from_n3(s, default=None, backend=None, nsm=None):
    r'''
    Creates the Identifier corresponding to the given n3 string.

        >>> from_n3('<http://ex.com/foo>') == URIRef('http://ex.com/foo')
        True
        >>> from_n3('"foo"@de') == Literal('foo', lang='de')
        True
        >>> from_n3('"""multi\nline\nstring"""@en') == Literal(
        ...     'multi\nline\nstring', lang='en')
        True
        >>> from_n3('42') == Literal(42)
        True
        >>> from_n3(Literal(42).n3()) == Literal(42)
        True
        >>> from_n3('"42"^^xsd:integer') == Literal(42)
        True
        >>> from rdflib import RDFS
        >>> from_n3('rdfs:label') == RDFS['label']
        True
        >>> nsm = NamespaceManager(Graph())
        >>> nsm.bind('dbpedia', 'http://dbpedia.org/resource/')
        >>> berlin = URIRef('http://dbpedia.org/resource/Berlin')
        >>> from_n3('dbpedia:Berlin', nsm=nsm) == berlin
        True

    '''
    if not s:
        return default
    if s.startswith('<'):
        return URIRef(s[1:-1])
    elif s.startswith('"'):
        if s.startswith('"""'):
            quotes = '"""'
        else:
            quotes = '"'
        value, rest = s.rsplit(quotes, 1)
        value = value[len(quotes):]  # strip leading quotes
        datatype = None
        language = None

        # as a given datatype overrules lang-tag check for it first
        dtoffset = rest.rfind('^^')
        if dtoffset >= 0:
            # found a datatype
            # datatype has to come after lang-tag so ignore everything before
            # see: http://www.w3.org/TR/2011/WD-turtle-20110809/
            # #prod-turtle2-RDFLiteral
            datatype = from_n3(rest[dtoffset + 2:], default, backend, nsm)
        else:
            if rest.startswith("@"):
                language = rest[1:]  # strip leading at sign

        value = value.replace(r'\"', '"')
        # Hack: this should correctly handle strings with either native unicode
        # characters, or \u1234 unicode escapes.
        value = value.encode("raw-unicode-escape").decode("unicode-escape")
        return Literal(value, language, datatype)
    elif s == 'true' or s == 'false':
        return Literal(s == 'true')
    elif s.isdigit():
        return Literal(int(s))
    elif s.startswith('{'):
        identifier = from_n3(s[1:-1])
        return QuotedGraph(backend, identifier)
    elif s.startswith('['):
        identifier = from_n3(s[1:-1])
        return Graph(backend, identifier)
    elif s.startswith("_:"):
        return BNode(s[2:])
    elif ':' in s:
        if nsm is None:
            # instantiate default NamespaceManager and rely on its defaults
            nsm = NamespaceManager(Graph())
        prefix, last_part = s.split(':', 1)
        ns = dict(nsm.namespaces())[prefix]
        return Namespace(ns)[last_part]
    else:
        return BNode(s)