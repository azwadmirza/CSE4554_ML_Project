    def get_metainfo(self):
        return bdecode_compat(base64.b64decode(self.config['state']['metainfo'].encode('utf-8')))