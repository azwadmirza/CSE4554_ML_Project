    def fromBox(self, name, strings, objects, proto):
        """
        Converts from box string representation to python. We read back too-long batched data and
        put it back together here.

        """
        value = StringIO()
        value.write(self.fromStringProto(strings.get(name), proto))
        for counter in count(2):
            # count from 2 upwards
            chunk = strings.get("%s.%d" % (name, counter))
            if chunk is None:
                break
            value.write(self.fromStringProto(chunk, proto))
        objects[name] = value.getvalue()