    def maybe_autosave(self, index):
        """
        Autosave a file if necessary.

        If the file is newly created (and thus not named by the user), do
        nothing.  If the current contents are the same as the autosave file
        (if it exists) or the original file (if no autosave filee exists),
        then do nothing. If the current contents are the same as the file on
        disc, but the autosave file is different, then remove the autosave
        file. In all other cases, autosave the file.

        Args:
            index (int): index into self.stack.data
        """
        finfo = self.stack.data[index]
        if finfo.newly_created:
            return
        orig_filename = finfo.filename
        orig_hash = self.file_hashes[orig_filename]
        new_hash = self.stack.compute_hash(finfo)
        if orig_filename in self.name_mapping:
            autosave_filename = self.name_mapping[orig_filename]
            autosave_hash = self.file_hashes[autosave_filename]
            if new_hash != autosave_hash:
                if new_hash == orig_hash:
                    self.remove_autosave_file(orig_filename)
                else:
                    self.autosave(finfo)
        else:
            if new_hash != orig_hash:
                self.autosave(finfo)