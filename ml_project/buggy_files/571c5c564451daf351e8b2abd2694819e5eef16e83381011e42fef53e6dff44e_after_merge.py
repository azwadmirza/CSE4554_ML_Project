    def createSaxChildren(self, sax_node, parent_v):
        '''Create vnodes for all children in sax_node.children.'''
        children = []
        for sax_child in sax_node.children:
            tnx = sax_child.tnx
            v = self.gnxDict.get(tnx)
            if v: # A clone. Don't look at the children.
                self.updateSaxClone(sax_child, parent_v, v)
            else:
                v = self.createSaxVnode(sax_child, parent_v)
                self.createSaxChildren(sax_child, v)
            children.append(v)
        parent_v.children = children
        for child in children:
            child.parents.append(parent_v)
        return children