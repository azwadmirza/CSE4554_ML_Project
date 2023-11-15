    def get_engineresumedata(self):
        return bdecode_compat(base64.b64decode(self.config['state']['engineresumedata'].encode('utf-8')))