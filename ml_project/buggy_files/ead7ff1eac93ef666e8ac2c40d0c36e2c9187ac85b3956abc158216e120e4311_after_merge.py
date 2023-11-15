    def get_file_hash(self, path_info):
        return HashInfo(self.PARAM_CHECKSUM, self.get_etag(path_info))