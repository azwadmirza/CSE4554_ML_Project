    def get_file_name(self):
        if not self.external_filename:
            assert self.object_store is not None, "Object Store has not been initialized for dataset %s" % self.id
            filename = self.object_store.get_filename(self)
            return filename
        else:
            filename = self.external_filename
        # Make filename absolute
        return os.path.abspath(filename)