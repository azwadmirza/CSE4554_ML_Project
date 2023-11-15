    def _process_property_change(self, msg):
        msg = super(FileInput, self)._process_property_change(msg)
        if 'value' in msg:
            header, content = msg['value'].split(",", 1)
            msg['mime_type'] = header.split(':')[1].split(';')[0]
            msg['value'] = b64decode(content)
        return msg