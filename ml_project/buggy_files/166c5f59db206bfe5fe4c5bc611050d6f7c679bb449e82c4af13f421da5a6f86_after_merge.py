    def get_file_hash(self, path_info):
        return HashInfo(self.PARAM_CHECKSUM, file_md5(path_info)[0])