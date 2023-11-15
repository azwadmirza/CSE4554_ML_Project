    def stats(self):
        """Return a stats dictionary of this result."""
        all_stats = dict(files=0, clean=0, unclean=0, violations=0)
        for path in self.paths:
            all_stats = self.sum_dicts(path.stats(), all_stats)
        if all_stats['files'] > 0:
            all_stats['avg per file'] = all_stats['violations'] * 1.0 / all_stats['files']
            all_stats['unclean rate'] = all_stats['unclean'] * 1.0 / all_stats['files']
        else:
            all_stats['avg per file'] = 0
            all_stats['unclean rate'] = 0
        all_stats['clean files'] = all_stats['clean']
        all_stats['unclean files'] = all_stats['unclean']
        all_stats['exit code'] = 65 if all_stats['violations'] > 0 else 0
        all_stats['status'] = 'FAIL' if all_stats['violations'] > 0 else 'PASS'
        return all_stats