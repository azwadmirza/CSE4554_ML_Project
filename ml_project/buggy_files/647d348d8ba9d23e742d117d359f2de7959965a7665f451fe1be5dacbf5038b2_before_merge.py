    def checkSiblings(self, p):
        '''Check the consistency of next and back links.'''
        back = p.back()
        next = p.next()
        if back:
            assert p == back.next(), 'p!=p.back().next(),  back: %s\nback.next: %s' % (
                back, back.next())
        if next:
            assert p == next.back(), 'p!=p.next().back, next: %s\nnext.back: %s' % (
                next, next.back())