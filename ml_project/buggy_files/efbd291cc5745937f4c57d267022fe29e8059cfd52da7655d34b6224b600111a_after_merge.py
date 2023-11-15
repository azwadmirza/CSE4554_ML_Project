    def iter_native(self, result, no_ack=True, **kwargs):
        self._ensure_not_eager()

        results = result.results
        if not results:
            raise StopIteration()

        # we tell the result consumer to put consumed results
        # into these buckets.
        bucket = deque()
        for node in results:
            if not hasattr(node, '_cache'):
                bucket.append(node)
            elif node._cache:
                bucket.append(node)
            else:
                self._collect_into(node, bucket)

        for _ in self._wait_for_pending(result, no_ack=no_ack, **kwargs):
            while bucket:
                node = bucket.popleft()
                if not hasattr(node, '_cache'):
                    yield node.id, node.children
                else:
                    yield node.id, node._cache
        while bucket:
            node = bucket.popleft()
            yield node.id, node._cache