    def _fetchable_partitions(self):
        fetchable = self._subscriptions.fetchable_partitions()
        if self._next_partition_records:
            fetchable.discard(self._next_partition_records.topic_partition)
        for fetch in self._completed_fetches:
            fetchable.discard(fetch.topic_partition)
        return fetchable