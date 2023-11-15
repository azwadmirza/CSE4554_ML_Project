    def _process_property_change(self, msg):
        msg = super(FileInput, self)._process_property_change(msg)
        if 'value' in msg:
            msg['value'] = b64decode(msg['value'])
        return msg