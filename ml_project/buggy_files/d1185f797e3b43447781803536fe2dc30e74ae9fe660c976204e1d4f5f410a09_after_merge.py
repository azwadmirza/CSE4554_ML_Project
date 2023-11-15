    def checkParentAndChildren(self, p):
        '''Check consistency of parent and child data structures.'''
        c = self
        
        def _assert(condition):
            return g._assert(condition, show_callers=False)

        def dump(p):
            if p and p.v:
                p.v.dump()
            elif p:
                print('<no p.v>')
            else:
                print('<no p>')
            if g.unitTesting:
                assert False, g.callers()
            
        if p.hasParent():
            n = p.childIndex()
            if not _assert(p == p.parent().moveToNthChild(n)):
                g.trace("p != parent().moveToNthChild(%s)" % (n))
                dump(p)
                dump(p.parent())
                return False
        if p.level() > 0 and not _assert(p.v.parents):
            g.trace("no parents")
            dump(p)
            return False
        for child in p.children():
            if not c.checkParentAndChildren(child):
                return False
            if not _assert(p == child.parent()):
                g.trace("p != child.parent()")
                dump(p)
                dump(child.parent())
                return False
        if p.hasNext():
            if not _assert(p.next().parent() == p.parent()):
                g.trace("p.next().parent() != p.parent()")
                dump(p.next().parent())
                dump(p.parent())
                return False
        if p.hasBack():
            if not _assert(p.back().parent() == p.parent()):
                g.trace("p.back().parent() != parent()")
                dump(p.back().parent())
                dump(p.parent())
                return False
        # Check consistency of parent and children arrays.
        # Every nodes gets visited, so a strong test need only check consistency
        # between p and its parent, not between p and its children.
        parent_v = p._parentVnode()
        n = p.childIndex()
        if not _assert(parent_v.children[n] == p.v):
            g.trace("parent_v.children[n] != p.v")
            parent_v.dump()
            p.v.dump()
            return False
        return True