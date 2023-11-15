    def log_artifacts(self, local_dir, artifact_path=None):
        dest_path = posixpath.join(self.path, artifact_path) \
            if artifact_path else self.path

        dest_path = posixpath.join(
            dest_path, os.path.split(local_dir)[1])
        dest_path_re = os.path.split(local_dir)[1]
        if artifact_path:
            dest_path_re = posixpath.join(
                artifact_path, os.path.split(local_dir)[1])

        local_dir = os.path.abspath(local_dir)
        for (root, _, filenames) in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path_re, rel_path)
            if not filenames:
                with self.get_ftp_client() as ftp:
                    self._mkdir(ftp, posixpath.join(self.path, upload_path))
            for f in filenames:
                if os.path.isfile(os.path.join(root, f)):
                    self.log_artifact(os.path.join(root, f), upload_path)