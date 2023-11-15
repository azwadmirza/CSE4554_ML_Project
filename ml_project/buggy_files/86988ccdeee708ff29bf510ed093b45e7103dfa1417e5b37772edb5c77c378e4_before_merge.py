    def get_file_hash(self, path_info):
        if path_info.scheme != self.scheme:
            raise NotImplementedError

        with self.ssh(path_info) as ssh:
            return self.PARAM_CHECKSUM, ssh.md5(path_info.path)