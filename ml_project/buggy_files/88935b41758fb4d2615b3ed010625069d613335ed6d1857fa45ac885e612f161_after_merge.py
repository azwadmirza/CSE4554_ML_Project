    def readSaxFile(self, theFile, fileName, silent, inClipboard, reassignIndices, s=None):
        '''Read the entire .leo file using the sax parser.'''
        dump = False and not g.unitTesting
        fc = self; c = fc.c
        # Pass one: create the intermediate nodes.
        saxRoot = fc.parse_leo_file(theFile, fileName,
            silent=silent, inClipboard=inClipboard, s=s)
        # Pass two: create the tree of vnodes from the intermediate nodes.
        if saxRoot:
            if dump: fc.dumpSaxTree(saxRoot, dummy=True)
            parent_v = c.hiddenRootNode
            children = fc.createSaxChildren(saxRoot, parent_v)
            assert c.hiddenRootNode.children == children
            v = children and children[0] or None
            return v
        else:
            return None