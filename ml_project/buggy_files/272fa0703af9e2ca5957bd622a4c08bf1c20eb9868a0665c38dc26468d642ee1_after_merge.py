    def create_unique_autosave_filename(self, filename, autosave_dir):
        """
        Create unique autosave file name for specified file name.

        The created autosave file name does not yet exist either in
        `self.name_mapping` or on disk.

        Args:
            filename (str): original file name
            autosave_dir (str): directory in which autosave files are stored
        """
        basename = osp.basename(filename)
        autosave_filename = osp.join(autosave_dir, basename)
        if (autosave_filename in self.name_mapping.values()
                or osp.exists(autosave_filename)):
            counter = 0
            root, ext = osp.splitext(basename)
            while (autosave_filename in self.name_mapping.values()
                   or osp.exists(autosave_filename)):
                counter += 1
                autosave_basename = '{}-{}{}'.format(root, counter, ext)
                autosave_filename = osp.join(autosave_dir, autosave_basename)
        return autosave_filename