    def toBox(self, name, strings, objects, proto):
        """
        Convert from python object to string box representation.
        we break up too-long data snippets into multiple batches here.

        """
        value = StringIO(objects[name])
        strings[name] = self.toStringProto(value.read(AMP_MAXLEN), proto)
        for counter in count(2):
            chunk = value.read(AMP_MAXLEN)
            if not chunk:
                break
            strings["%s.%d" % (name, counter)] = self.toStringProto(chunk, proto)