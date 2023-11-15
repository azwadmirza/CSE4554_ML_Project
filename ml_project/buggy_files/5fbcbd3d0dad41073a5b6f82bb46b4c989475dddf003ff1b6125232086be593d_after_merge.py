    def _process_param_change(self, msg):
        msg = super(FileInput, self)._process_param_change(msg)
        if 'value' in msg:
            msg.pop('value')
        if 'mime_type' in msg:
            msg.pop('mime_type')
        return msg