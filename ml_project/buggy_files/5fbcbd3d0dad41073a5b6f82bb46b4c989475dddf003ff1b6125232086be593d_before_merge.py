    def _process_param_change(self, msg):
        msg = super(FileInput, self)._process_param_change(msg)
        if 'value' in msg:
            if self.mime_type:
                template = 'data:{mime};base64,{data}'
                data = b64encode(msg['value'])
                msg['value'] = template.format(data=data.decode('utf-8'),
                                               mime=self.mime_type)
            else:
                msg['value'] = ''
        return msg