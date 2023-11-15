    def readFile(self, fileName, root):
        '''
        Read the file from the cache if possible.
        Return (s,ok,key)
        '''
        trace = False and not g.unitTesting
        showHits = False
        showLines = False
        showList = False
        sfn = g.shortFileName(fileName)
        if not g.enableDB:
            if trace: g.trace('g.enableDB is False', fileName)
            return '', False, None
        if trace: g.trace('=====', root.v.gnx, 'children', root.numberOfChildren(), fileName)
        s = g.readFileIntoEncodedString(fileName, silent=True)
        if s is None:
            if trace: g.trace('empty file contents', fileName)
            return s, False, None
        assert not g.isUnicode(s)
        if trace and showLines:
            for i, line in enumerate(g.splitLines(s)):
                print('%3d %s' % (i, repr(line)))
        # There will be a bug if s is not already an encoded string.
        key = self.fileKey(fileName, s, requireEncodedString=True)
            # Fix bug #385: use the full fileName, not root.h.
        ok = self.db and key in self.db
        if ok:
            if trace and showHits: g.trace('cache hit', key[-6:], sfn)
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = self.db.get(key)
            if trace and showList:
                g.printList(list(g.flatten_list(aList)))
            self.collectChangedNodes(root.v, aList, fileName)
            self.createOutlineFromCacheList2(root.v, aList)
            #self.createOutlineFromCacheList(root.v, aList, fileName=fileName)
        elif trace:
            g.trace('cache miss', key[-6:], sfn)
        return s, ok, key