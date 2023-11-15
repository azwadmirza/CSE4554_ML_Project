    def get_file_hash(self, path_info):
        return self.PARAM_CHECKSUM, self.get_etag(path_info)