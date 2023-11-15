    def teardown_handles(self):
        for g in ('whiskers', 'fliers', 'medians', 'boxes', 'caps', 'means'):
            for v in self.handles.get(g, []):
                v.remove()