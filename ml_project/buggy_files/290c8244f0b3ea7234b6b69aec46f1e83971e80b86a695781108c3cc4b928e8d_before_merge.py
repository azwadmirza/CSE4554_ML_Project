    def list_artifacts(self, path=None):
        with self.get_ftp_client() as ftp:
            artifact_dir = self.path
            list_dir = posixpath.join(artifact_dir, path) if path else artifact_dir
            if not self._is_dir(ftp, list_dir):
                return []
            artifact_files = ftp.nlst(list_dir)
            artifact_files = list(filter(lambda x: x != "." and x != "..", artifact_files))
            infos = []
            for file_name in artifact_files:
                file_path = (file_name if path is None
                             else posixpath.join(path, file_name))
                full_file_path = posixpath.join(list_dir, file_name)
                if self._is_dir(ftp, full_file_path):
                    infos.append(FileInfo(file_path, True, None))
                else:
                    size = self._size(ftp, full_file_path)
                    infos.append(FileInfo(file_path, False, size))
        return infos