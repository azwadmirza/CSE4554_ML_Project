    def put_if_absent(self, k, v, use_serialize=True):
        return self.__client.put_if_absent(self, k, v, use_serialize=use_serialize)