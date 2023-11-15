    def _collect_attrs(self, name, obj):
        """Collect all the attributes for the provided file object.
        """
        for key in obj.ncattrs():
            value = getattr(obj, key)
            fc_key = "{}/attr/{}".format(name, key)
            try:
                self.file_content[fc_key] = np2str(value)
            except ValueError:
                self.file_content[fc_key] = value