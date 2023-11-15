    def checkSiblings(self, p):
        '''Check the consistency of next and back links.'''
        back = p.back()
        next = p.next()
        if back:
            if not g._assert(p == back.next()):
                g.trace('p!=p.back().next(),  back: %s\nback.next: %s' % (
                    back, back.next()))
                return False
        if next:
            if not g._assert(p == next.back()):
                g.trace('p!=p.next().back, next: %s\nnext.back: %s' % (
                    next, next.back()))
                return False
        return True