    def delete(self, k, use_serialize=True):
        return self.__client.delete(self, k, use_serialize=use_serialize)