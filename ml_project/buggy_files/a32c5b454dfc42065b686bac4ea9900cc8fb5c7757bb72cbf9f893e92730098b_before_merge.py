    def fromBox(self, name, strings, objects, proto):
        """
        Converts from box representation to python. We
        group very long data into batches.
        """
        value = StringIO()
        value.write(strings.get(name))
        for counter in count(2):
            # count from 2 upwards
            chunk = strings.get("%s.%d" % (name, counter))
            if chunk is None:
                break
            value.write(chunk)
        objects[name] = value.getvalue()