def parse_xml( fname ):
    """Returns a parsed xml tree"""
    # handle deprecation warning for XMLParsing a file with DOCTYPE
    class DoctypeSafeCallbackTarget( ElementTree.TreeBuilder ):
        def doctype( *args ):
            pass
    tree = ElementTree.ElementTree()
    root = tree.parse( fname, parser=ElementTree.XMLParser( target=DoctypeSafeCallbackTarget() ) )
    ElementInclude.include( root )
    return tree