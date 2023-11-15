    def map(self, func):
        _intermediate_result = _EggRoll.get_instance().map(self, func)
        return _intermediate_result.save_as(str(uuid.uuid1()), _intermediate_result._namespace,
                                            partition=_intermediate_result._partitions)