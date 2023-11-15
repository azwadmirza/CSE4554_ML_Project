    def save_as(self, name, namespace, partition=None, use_serialize=True):
        if partition is None:
            partition = self._partitions
        dup = self.__client.table(name, namespace, partition=partition)
        dup.put_all(self.collect(use_serialize=use_serialize), use_serialize=use_serialize)
        return dup