    def _set_queue_attributes(self, path, req_data, headers):
        queue_url = self._queue_url(path, req_data, headers)
        attrs = self._format_attributes(req_data)
        # select only the attributes in UNSUPPORTED_ATTRIBUTE_NAMES
        attrs = dict([(k, v) for k, v in attrs.items() if k in UNSUPPORTED_ATTRIBUTE_NAMES])
        QUEUE_ATTRIBUTES[queue_url] = QUEUE_ATTRIBUTES.get(queue_url) or {}
        QUEUE_ATTRIBUTES[queue_url].update(attrs)