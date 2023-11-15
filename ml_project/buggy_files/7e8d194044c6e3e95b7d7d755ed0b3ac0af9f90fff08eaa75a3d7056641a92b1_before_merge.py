    def iter_filters(self, block_end=False):
        queue = deque(self.filters)
        while queue:
            f = queue.popleft()
            if f and f.type in ('or', 'and', 'not'):
                if block_end:
                    queue.appendleft(None)
                for gf in f.filters:
                    queue.appendleft(gf)
            yield f