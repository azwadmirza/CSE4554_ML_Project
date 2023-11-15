    def _load_inventory_file(self, path, loader):
        '''
        helper function, which loads the file and gets the
        basename of the file without the extension
        '''

        if loader.is_directory(path):
            data = dict()

            try:
                names = loader.list_directory(path)
            except os.error as err:
                raise AnsibleError("This folder cannot be listed: %s: %s." % (path, err.strerror))

            # evaluate files in a stable order rather than whatever
            # order the filesystem lists them.
            names.sort()

            # do not parse hidden files or dirs, e.g. .svn/
            paths = [os.path.join(path, name) for name in names if not name.startswith('.')]
            for p in paths:
                _found, results = self._load_inventory_file(path=p, loader=loader)
                if results is not None:
                    data = combine_vars(data, results)

        else:
            file_name, ext = os.path.splitext(path)
            data = None
            if not ext or ext not in C.YAML_FILENAME_EXTENSIONS:
                for test_ext in C.YAML_FILENAME_EXTENSIONS:
                    new_path = path + test_ext
                    if loader.path_exists(new_path):
                        data = loader.load_from_file(new_path)
                        break
            else:
                if loader.path_exists(path):
                    data = loader.load_from_file(path)

        rval = AnsibleInventoryVarsData()
        rval.path = path
        if data is not None:
            rval.update(data)
        return rval