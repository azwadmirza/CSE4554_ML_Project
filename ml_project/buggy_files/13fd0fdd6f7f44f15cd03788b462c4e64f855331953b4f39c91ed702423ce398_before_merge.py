    def get_engineresumedata(self):
        return lt.bdecode(base64.b64decode(self.config['state']['engineresumedata'].encode('utf-8')))