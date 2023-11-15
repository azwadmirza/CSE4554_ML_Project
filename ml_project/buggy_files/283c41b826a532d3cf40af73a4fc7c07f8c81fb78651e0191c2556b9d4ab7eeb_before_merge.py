    def put(self, k, v, use_serialize=True):
        self.__client.put(self, k, v, use_serialize=use_serialize)