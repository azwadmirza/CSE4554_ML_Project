    def get_file_hash(self, path_info):
        with self._get_obj(path_info) as obj:
            return HashInfo(self.PARAM_CHECKSUM, obj.e_tag.strip('"'))