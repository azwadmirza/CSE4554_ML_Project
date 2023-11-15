    def get_metainfo(self):
        return lt.bdecode(base64.b64decode(self.config['state']['metainfo'].encode('utf-8')))