    def join(self, other, func):
        if other._partitions != self._partitions:
            if other.count() > self.count():
                return self.save_as(str(uuid.uuid1()), _EggRoll.get_instance().job_id, partition=other._partitions).join(other,
                                                                                                               func)
            else:
                return self.join(other.save_as(str(uuid.uuid1()), _EggRoll.get_instance().job_id, partition=self._partitions),
                                 func)
        return _EggRoll.get_instance().join(self, other, func)