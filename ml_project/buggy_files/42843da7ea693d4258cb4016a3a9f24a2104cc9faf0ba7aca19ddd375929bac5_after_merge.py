    def checkLinks(self):
        '''Check the consistency of all links in the outline.'''
        c = self
        t1 = time.time()
        count, errors = 0, 0
        for p in c.safe_all_positions():
            count += 1
            # try:
            if not c.checkThreadLinks(p):
                errors += 1
                break
            if not c.checkSiblings(p):
                errors += 1
                break
            if not c.checkParentAndChildren(p):
                errors += 1
                break
            # except AssertionError:
                # errors += 1
                # junk, value, junk = sys.exc_info()
                # g.error("test failed at position %s\n%s" % (repr(p), value))
        t2 = time.time()
        g.es_print('check-links: %4.2f sec. %s %s nodes' % (
            t2 - t1, c.shortFileName(), count), color='blue')
        return errors