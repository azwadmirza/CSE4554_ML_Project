    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise Exception(
                "term '%s' not in namespace '%s'" % (name, self))
        else:
            return uri