    def compute_qname(self, uri, generate=True):
        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            namespace = URIRef(namespace)
            prefix = self.store.prefix(namespace)
            if prefix is None:
                if not generate:
                    raise Exception(
                        "No known prefix for %s and generate=False")
                num = 1
                while 1:
                    prefix = "ns%s" % num
                    if not self.store.namespace(prefix):
                        break
                    num += 1
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]