    def readFileFromClipboard(self, s):
        """
        Recreate a file from a string s, and return its hidden vnode.
        
        Unlike readFile above, this does not affect splitter sizes.
        """
        v, g_element = self.readWithElementTree(path=None, s=s)
        #
        # Fix bug #1111: ensure that all outlines have at least one node.
        if not v.children:
            new_vnode = leoNodes.VNode(context=self.c)
            new_vnode.h = 'newHeadline'
            v.children = [new_vnode]
        return v