    def _collect_attrs(self, name, obj):
        """Collect all the attributes for the provided file object.
        """
        for key in obj.ncattrs():
            value = getattr(obj, key)
            value = np.squeeze(value)
            if issubclass(value.dtype.type, str) or np.issubdtype(value.dtype, np.character):
                self.file_content["{}/attr/{}".format(name, key)] = str(value)
            else:
                self.file_content["{}/attr/{}".format(name, key)] = value