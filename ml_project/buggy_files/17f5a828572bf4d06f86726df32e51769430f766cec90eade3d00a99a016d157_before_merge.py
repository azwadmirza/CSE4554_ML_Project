    def readFile(self, path):
        """Read the file, change splitter ratiors, and return its hidden vnode."""
        with open(path, 'rb') as f:
            s = f.read()
        v, g_element = self.readWithElementTree(path, s)
        self.scanGlobals(g_element)
            # Fix #1047: only this method changes splitter sizes.
        #
        # Fix bug #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v