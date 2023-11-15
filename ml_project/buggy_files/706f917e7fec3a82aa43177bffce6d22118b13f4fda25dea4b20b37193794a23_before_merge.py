    def getLeoOutlineFromClipboard(self, s, reassignIndices=True): ###, tempOutline=False):
        '''Read a Leo outline from string s in clipboard format.'''
        ###
            # if tempOutline:
                # g.trace('===== tempOutline is True', g.callers())
                # if g.unitTesting: assert False
        c = self.c
        current = c.p
        if not current:
            g.trace('no c.p')
            return None
        check = not reassignIndices
        self.initReadIvars()
        # Save the hidden root's children.
        children = c.hiddenRootNode.children
        # 2011/12/12: save and clear gnxDict.
        # This ensures that new indices will be used for all nodes.
        if reassignIndices: ### or tempOutline:
            oldGnxDict = self.gnxDict
            self.gnxDict = {}
        else:
            # All pasted nodes should already have unique gnx's.
            ni = g.app.nodeIndices
            for v in c.all_unique_nodes():
                ni.check_gnx(c, v.fileIndex, v)
        self.usingClipboard = True
        try:
            # This encoding must match the encoding used in putLeoOutline.
            s = g.toEncodedString(s, self.leo_file_encoding, reportErrors=True)
            # readSaxFile modifies the hidden root.
            v = self.readSaxFile(
                theFile=None, fileName='<clipboard>',
                silent=True, # don't tell about stylesheet elements.
                inClipboard=True, reassignIndices=reassignIndices, s=s)
            if not v:
                return g.es("the clipboard is not valid ", color="blue")
        finally:
            self.usingClipboard = False
        # Restore the hidden root's children
        c.hiddenRootNode.children = children
        # Unlink v from the hidden root.
        v.parents.remove(c.hiddenRootNode)
        p = leoNodes.Position(v)
        # Important: we must not adjust links when linking v
        # into the outline.  The read code has already done that.
        if current.hasChildren() and current.isExpanded():
            if check and not self.checkPaste(current, p):
                return None
            p._linkAsNthChild(current, 0, adjust=False)
        else:
            if check and not self.checkPaste(current.parent(), p):
                return None
            p._linkAfter(current, adjust=False)
        ###
        c.dumpOutline()
        ###
            # if tempOutline:
                # self.gnxDict = oldGnxDict
            # elif reassignIndices:
        if reassignIndices:
            self.gnxDict = oldGnxDict
            ni = g.app.nodeIndices
            for p2 in p.self_and_subtree():
                v = p2.v
                index = ni.getNewIndex(v)
                if g.trace_gnxDict:
                    g.trace(c.shortFileName(), '**restoring**', index, v)
        c.selectPosition(p)
        self.initReadIvars()
        return p