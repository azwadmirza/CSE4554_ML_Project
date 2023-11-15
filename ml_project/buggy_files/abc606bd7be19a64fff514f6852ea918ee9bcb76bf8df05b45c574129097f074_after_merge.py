    def checkThreadLinks(self, p):
        '''Check consistency of threadNext & threadBack links.'''
        threadBack = p.threadBack()
        threadNext = p.threadNext()
        if threadBack:
            if not g._assert(p == threadBack.threadNext()):
                g.trace("p!=p.threadBack().threadNext()")
                return False
        if threadNext:
            if not g._assert(p == threadNext.threadBack()):
                g.trace("p!=p.threadNext().threadBack()")
                return False
        return True