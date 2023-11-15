    def _add_queue_attributes(self, path, req_data, content_str, headers):
        flags = re.MULTILINE | re.DOTALL
        queue_url = self._queue_url(path, req_data, headers)
        regex = r'(.*<GetQueueAttributesResult>)(.*)(</GetQueueAttributesResult>.*)'
        attrs = re.sub(regex, r'\2', content_str, flags=flags)
        for key, value in QUEUE_ATTRIBUTES.get(queue_url, {}).items():
            if not re.match(r'<Name>\s*%s\s*</Name>' % key, attrs, flags=flags):
                attrs += '<Attribute><Name>%s</Name><Value>%s</Value></Attribute>' % (key, value)
        content_str = (re.sub(regex, r'\1', content_str, flags=flags) +
            attrs + re.sub(regex, r'\3', content_str, flags=flags))
        return content_str