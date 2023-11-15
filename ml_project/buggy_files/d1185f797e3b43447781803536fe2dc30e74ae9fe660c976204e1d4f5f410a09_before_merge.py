    def checkParentAndChildren(self, p):
        '''Check consistency of parent and child data structures.'''
        # Check consistency of parent and child links.
        if p.hasParent():
            n = p.childIndex()
            assert p == p.parent().moveToNthChild(n), "p!=parent.moveToNthChild"
        for child in p.children():
            assert p == child.parent(), "p!=child.parent"
        if p.hasNext():
            assert p.next().parent() == p.parent(), "next.parent!=parent"
        if p.hasBack():
            assert p.back().parent() == p.parent(), "back.parent!=parent"
        # Check consistency of parent and children arrays.
        # Every nodes gets visited, so a strong test need only check consistency
        # between p and its parent, not between p and its children.
        parent_v = p._parentVnode()
        n = p.childIndex()
        assert parent_v.children[n] == p.v, 'fail 1'