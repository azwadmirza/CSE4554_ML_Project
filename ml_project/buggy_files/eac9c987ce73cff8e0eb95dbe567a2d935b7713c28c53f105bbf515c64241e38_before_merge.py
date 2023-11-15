def generate_gml(G, stringizer=None):
    r"""Generate a single entry of the graph `G` in GML format.

    Parameters
    ----------
    G : NetworkX graph
        The graph to be converted to GML.

    stringizer : callable, optional
        A `stringizer` which converts non-int/non-float/non-dict values into
        strings. If it cannot convert a value into a string, it should raise a
        `ValueError` to indicate that. Default value: None.

    Returns
    -------
    lines: generator of strings
        Lines of GML data. Newlines are not appended.

    Raises
    ------
    NetworkXError
        If `stringizer` cannot convert a value into a string, or the value to
        convert is not a string while `stringizer` is None.

    See Also
    --------
    literal_stringizer

    Notes
    -----
    Graph attributes named 'directed', 'multigraph', 'node' or
    'edge', node attributes named 'id' or 'label', edge attributes
    named 'source' or 'target' (or 'key' if `G` is a multigraph)
    are ignored because these attribute names are used to encode the graph
    structure.

    GML files are stored using a 7-bit ASCII encoding with any extended
    ASCII characters (iso8859-1) appearing as HTML character entities.
    Without specifying a `stringizer`/`destringizer`, the code is capable of
    handling `int`/`float`/`str`/`dict`/`list` data as required by the GML
    specification.  For other data types, you need to explicitly supply a
    `stringizer`/`destringizer`.

    For additional documentation on the GML file format, please see the
    `GML website <http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html>`_.

    See the module docstring :mod:`networkx.readwrite.gml` for additional details.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_node("1")
    >>> print("\n".join(nx.generate_gml(G)))
    graph [
      node [
        id 0
        label "1"
      ]
    ]
    >>> G = nx.OrderedMultiGraph([("a", "b"), ("a", "b")])
    >>> print("\n".join(nx.generate_gml(G)))
    graph [
      multigraph 1
      node [
        id 0
        label "a"
      ]
      node [
        id 1
        label "b"
      ]
      edge [
        source 0
        target 1
        key 0
      ]
      edge [
        source 0
        target 1
        key 1
      ]
    ]
    """
    valid_keys = re.compile('^[A-Za-z][0-9A-Za-z]*$')

    def stringize(key, value, ignored_keys, indent, in_list=False):
        if not isinstance(key, (str, unicode)):
            raise NetworkXError('%r is not a string' % (key,))
        if not valid_keys.match(key):
            raise NetworkXError('%r is not a valid key' % (key,))
        if not isinstance(key, str):
            key = str(key)
        if key not in ignored_keys:
            if isinstance(value, (int, long)):
                if key == 'label':
                    yield indent + key + ' "' + str(value) + '"'
                else:
                    yield indent + key + ' ' + str(value)
            elif isinstance(value, float):
                text = repr(value).upper()
                # GML requires that a real literal contain a decimal point, but
                # repr may not output a decimal point when the mantissa is
                # integral and hence needs fixing.
                epos = text.rfind('E')
                if epos != -1 and text.find('.', 0, epos) == -1:
                    text = text[:epos] + '.' + text[epos:]
                if key == 'label':
                    yield indent + key + ' "' + test + '"'
                else:
                    yield indent + key + ' ' + text
            elif isinstance(value, dict):
                yield indent + key + ' ['
                next_indent = indent + '  '
                for key, value in value.items():
                    for line in stringize(key, value, (), next_indent):
                        yield line
                yield indent + ']'
            elif isinstance(value, list) and value and not in_list:
                next_indent = indent + '  '
                for value in value:
                    for line in stringize(key, value, (), next_indent, True):
                        yield line
            else:
                if stringizer:
                    try:
                        value = stringizer(value)
                    except ValueError:
                        raise NetworkXError(
                            '%r cannot be converted into a string' % (value,))
                if not isinstance(value, (str, unicode)):
                    raise NetworkXError('%r is not a string' % (value,))
                yield indent + key + ' "' + escape(value) + '"'

    multigraph = G.is_multigraph()
    yield 'graph ['

    # Output graph attributes
    if G.is_directed():
        yield '  directed 1'
    if multigraph:
        yield '  multigraph 1'
    ignored_keys = {'directed', 'multigraph', 'node', 'edge'}
    for attr, value in G.graph.items():
        for line in stringize(attr, value, ignored_keys, '  '):
            yield line

    # Output node data
    node_id = dict(zip(G, range(len(G))))
    ignored_keys = {'id', 'label'}
    for node, attrs in G.node.items():
        yield '  node ['
        yield '    id ' + str(node_id[node])
        for line in stringize('label', node, (), '    '):
            yield line
        for attr, value in attrs.items():
            for line in stringize(attr, value, ignored_keys, '    '):
                yield line
        yield '  ]'

    # Output edge data
    ignored_keys = {'source', 'target'}
    kwargs = {'data': True}
    if multigraph:
        ignored_keys.add('key')
        kwargs['keys'] = True
    for e in G.edges(**kwargs):
        yield '  edge ['
        yield '    source ' + str(node_id[e[0]])
        yield '    target ' + str(node_id[e[1]])
        if multigraph:
            for line in stringize('key', e[2], (), '    '):
                yield line
        for attr, value in e[-1].items():
            for line in stringize(attr, value, ignored_keys, '    '):
                yield line
        yield '  ]'
    yield ']'