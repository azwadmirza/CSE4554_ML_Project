    def publish(self, source, data, metadata=None):
        if metadata is None:
            metadata = {}
        self._validate_data(source, data, metadata)
        content = {}
        content['source'] = source
        _encode_binary(data)
        content['data'] = data
        content['metadata'] = metadata
        self.session.send(
            self.pub_socket, u'display_data', json_clean(content),
            parent=self.parent_header
        )