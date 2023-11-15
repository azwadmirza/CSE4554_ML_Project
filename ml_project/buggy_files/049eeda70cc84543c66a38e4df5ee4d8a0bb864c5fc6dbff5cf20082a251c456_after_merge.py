    def put_all(self, kv_list: Iterable, use_serialize=True):
        return _EggRoll.get_instance().put_all(self, kv_list, use_serialize=use_serialize)