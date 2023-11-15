    def _add_queue_attributes(self, req_data, content_str):
        flags = re.MULTILINE | re.DOTALL
        queue_url = req_data['QueueUrl'][0]
        regex = r'(.*<GetQueueAttributesResult>)(.*)(</GetQueueAttributesResult>.*)'
        attrs = re.sub(regex, r'\2', content_str, flags=flags)
        for key, value in QUEUE_ATTRIBUTES.get(queue_url, {}).items():
            if not re.match(r'<Name>\s*%s\s*</Name>' % key, attrs, flags=flags):
                attrs += '<Attribute><Name>%s</Name><Value>%s</Value></Attribute>' % (key, value)
        content_str = (re.sub(regex, r'\1', content_str, flags=flags) +
            attrs + re.sub(regex, r'\3', content_str, flags=flags))
        return content_str