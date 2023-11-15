    def _unique_name(self, basename, ext, existing, force=False):
        """
        Find a unique basename for a new file/key where existing is
        either a list of (basename, ext) pairs or an absolute path to
        a directory.

        By default, uniqueness is enforced dependning on the state of
        the unique_name parameter (for export names). If force is
        True, this parameter is ignored and uniqueness is guaranteed.
        """
        skip = False if force else (not self.unique_name)
        if skip: return (basename, ext)
        ext = '' if ext is None else ext
        if isinstance(existing, str):
            split = [os.path.splitext(el)
                     for el in os.listdir(os.path.abspath(existing))]
            existing = [(n, ex if not ex else ex[1:]) for (n, ex) in split]
        new_name, counter = basename, 1
        while (new_name, ext) in existing:
            new_name = basename+'-'+str(counter)
            counter += 1
        return (new_name, ext)