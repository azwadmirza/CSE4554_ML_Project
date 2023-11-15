    def join(self, other, func):
        if other._partitions != self._partitions:
            if other.count() > self.count():
                return self.save_as(str(uuid.uuid1()), self.__client.job_id, partition=other._partitions).join(other,
                                                                                                               func)
            else:
                return self.join(other.save_as(str(uuid.uuid1()), self.__client.job_id, partition=self._partitions),
                                 func)
        return self.__client.join(self, other, func)