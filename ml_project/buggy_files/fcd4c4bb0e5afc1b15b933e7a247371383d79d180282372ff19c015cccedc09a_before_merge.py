    def get_extra_files_path(self):
        # Unlike get_file_name - external_extra_files_path is not backed by an
        # actual database column so if SA instantiates this object - the
        # attribute won't exist yet.
        if not getattr(self, "external_extra_files_path", None):
            return self.object_store.get_filename(self, dir_only=True, extra_dir=self._extra_files_rel_path)
        else:
            return os.path.abspath(self.external_extra_files_path)