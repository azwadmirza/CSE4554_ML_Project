    def _collect_attrs(self, name, attrs):
        for key, value in six.iteritems(attrs):
            value = np.squeeze(value)
            fc_key = "{}/attr/{}".format(name, key)
            try:
                self.file_content[fc_key] = np2str(value)
            except ValueError:
                self.file_content[fc_key] = value