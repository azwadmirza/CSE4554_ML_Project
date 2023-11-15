def parse_xml( fname ):
    """Returns a parsed xml tree"""
    # handle deprecation warning for XMLParsing a file with DOCTYPE
    class DoctypeSafeCallbackTarget( ElementTree.TreeBuilder ):
        def doctype( *args ):
            pass
    tree = ElementTree.ElementTree()
    try:
        root = tree.parse( fname, parser=ElementTree.XMLParser( target=DoctypeSafeCallbackTarget() ) )
    except ParseError:
        log.exception("Error parsing file %s", fname)
        raise
    ElementInclude.include( root )
    return tree