    def _fetchable_partitions(self):
        fetchable = self._subscriptions.fetchable_partitions()
        # do not fetch a partition if we have a pending fetch response to process
        current = self._next_partition_records
        pending = copy.copy(self._completed_fetches)
        if current:
            fetchable.discard(current.topic_partition)
        for fetch in pending:
            fetchable.discard(fetch.topic_partition)
        return fetchable