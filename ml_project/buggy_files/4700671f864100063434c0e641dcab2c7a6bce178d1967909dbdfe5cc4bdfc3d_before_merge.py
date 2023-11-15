    def get(self, k, use_serialize=True):
        return self.__client.get(self, k, use_serialize=use_serialize)