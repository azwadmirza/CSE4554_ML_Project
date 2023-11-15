    def toBox(self, name, strings, objects, proto):
        """
        Convert from data to box. We handled too-long
        batched data and put it together here.
        """
        value = StringIO(objects[name])
        strings[name] = value.read(AMP_MAXLEN)
        for counter in count(2):
            chunk = value.read(AMP_MAXLEN)
            if not chunk:
                break
            strings["%s.%d" % (name, counter)] = chunk