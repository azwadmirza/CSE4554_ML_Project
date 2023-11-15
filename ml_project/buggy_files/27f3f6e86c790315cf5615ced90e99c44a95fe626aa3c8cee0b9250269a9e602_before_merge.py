    def _shrink_down(self, collect=True):
        resource = self._resource
        # Items to the left are last recently used, so we remove those first.
        with resource.mutex:
            while len(resource.queue) > self.limit:
                R = resource.queue.popleft()
                if collect:
                    self.collect_resource(R)