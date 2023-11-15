    def put_all(self, kv_list: Iterable, use_serialize=True):
        return self.__client.put_all(self, kv_list, use_serialize=use_serialize)