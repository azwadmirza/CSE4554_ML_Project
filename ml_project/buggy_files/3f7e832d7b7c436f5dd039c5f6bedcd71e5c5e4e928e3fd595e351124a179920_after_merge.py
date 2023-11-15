    def compute_last_index(self, c):
        '''Scan the entire leo outline to compute ni.last_index.'''
        trace = False and not g.unitTesting
        verbose = True # Report only if lastIndex was changed.
        if trace: t1 = time.time()
        ni = self
        old_lastIndex = self.lastIndex
        # Partial, experimental, fix for #658.
        # Do not change self.lastIndex here!
            # self.lastIndex = 0
        for v in c.all_unique_nodes():
            gnx = v.fileIndex
            if trace and verbose: g.trace(gnx)
            if gnx:
                id_, t, n = self.scanGnx(gnx)
                if t == ni.timeString and n is not None:
                    try:
                        n = int(n)
                        self.lastIndex = max(self.lastIndex, n)
                        if trace and verbose: g.trace(n, gnx)
                    except Exception:
                        g.es_exception()
                        self.lastIndex += 1
        if trace:
            changed = self.lastIndex > old_lastIndex
            t2 = time.time()
            if verbose:
                g.trace('========== time %4.2f changed: %5s lastIndex: old: %s new: %s' % (
                    t2 - t1, changed, old_lastIndex, self.lastIndex))
            elif changed:
                g.trace('========== time %4.2f lastIndex: old: %s new: %s' % (
                    t2 - t1, old_lastIndex, self.lastIndex))