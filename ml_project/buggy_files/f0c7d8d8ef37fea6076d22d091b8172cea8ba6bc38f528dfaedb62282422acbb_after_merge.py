    def full_delete(self):
        """Remove the file and extra files, marks deleted and purged"""
        # os.unlink( self.file_name )
        try:
            self.object_store.delete(self)
        except galaxy.exceptions.ObjectNotFound:
            pass
        if self.object_store.exists(self, extra_dir=self._extra_files_rel_path, dir_only=True):
            self.object_store.delete(self, entire_dir=True, extra_dir=self._extra_files_rel_path, dir_only=True)
        # TODO: purge metadata files
        self.deleted = True
        self.purged = True