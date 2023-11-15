    def checkThreadLinks(self, p):
        '''Check consistency of threadNext & threadBack links.'''
        threadBack = p.threadBack()
        threadNext = p.threadNext()
        if threadBack:
            assert p == threadBack.threadNext(), "p!=p.threadBack().threadNext()"
        if threadNext:
            assert p == threadNext.threadBack(), "p!=p.threadNext().threadBack()"