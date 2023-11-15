    def run(self):
        """ Add a new root (parent) directory to Medusa """

        self.location = unquote_plus(self.location)
        location_matched = 0
        index = 0

        # disallow adding/setting an invalid dir
        if not os.path.isdir(self.location):
            return _responds(RESULT_FAILURE, msg='Location is invalid')

        root_dirs = []

        if app.ROOT_DIRS == '':
            self.default = 1
        else:
            root_dirs = app.ROOT_DIRS
            index = int(app.ROOT_DIRS[0])
            root_dirs.pop(0)
            # clean up the list - replace %xx escapes by their single-character equivalent
            root_dirs = [unquote_plus(x) for x in root_dirs]
            for x in root_dirs:
                if x == self.location:
                    location_matched = 1
                    if self.default == 1:
                        index = root_dirs.index(self.location)
                    break

        if location_matched == 0:
            if self.default == 1:
                root_dirs.insert(0, self.location)
            else:
                root_dirs.append(self.location)

        root_dirs_new = [unquote_plus(x) for x in root_dirs]
        root_dirs_new.insert(0, index)
        root_dirs_new = '|'.join(text_type(x) for x in root_dirs_new)

        app.ROOT_DIRS = root_dirs_new
        return _responds(RESULT_SUCCESS, _get_root_dirs(), msg='Root directories updated')