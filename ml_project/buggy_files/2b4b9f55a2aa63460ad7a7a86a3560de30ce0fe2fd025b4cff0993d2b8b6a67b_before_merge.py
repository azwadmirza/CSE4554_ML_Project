    def mapPartitions(self, func):
        return self.__client.map_partitions(self, func)