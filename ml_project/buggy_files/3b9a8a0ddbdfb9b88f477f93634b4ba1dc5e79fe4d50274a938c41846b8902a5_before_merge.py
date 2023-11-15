    def _set_queue_attributes(self, req_data):
        queue_url = req_data['QueueUrl'][0]
        attrs = self._format_attributes(req_data)
        # select only the attributes in UNSUPPORTED_ATTRIBUTE_NAMES
        attrs = dict([(k, v) for k, v in attrs.items() if k in UNSUPPORTED_ATTRIBUTE_NAMES])
        QUEUE_ATTRIBUTES[queue_url] = QUEUE_ATTRIBUTES.get(queue_url) or {}
        QUEUE_ATTRIBUTES[queue_url].update(attrs)