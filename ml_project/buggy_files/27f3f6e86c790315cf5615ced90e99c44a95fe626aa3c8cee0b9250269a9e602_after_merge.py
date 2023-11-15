    def _shrink_down(self, collect=True):
        class Noop:
            def __enter__(self):
                pass

            def __exit__(self, type, value, traceback):
                pass

        resource = self._resource
        # Items to the left are last recently used, so we remove those first.
        with getattr(resource, 'mutex', Noop()):
            while len(resource.queue) > self.limit:
                R = resource.queue.popleft()
                if collect:
                    self.collect_resource(R)