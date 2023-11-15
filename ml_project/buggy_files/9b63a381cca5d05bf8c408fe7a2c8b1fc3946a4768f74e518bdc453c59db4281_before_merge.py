    def _collect_attrs(self, name, attrs):
        for key, value in six.iteritems(attrs):
            value = np.squeeze(value)
            self.file_content["{}/attr/{}".format(name, key)] = np2str(value)