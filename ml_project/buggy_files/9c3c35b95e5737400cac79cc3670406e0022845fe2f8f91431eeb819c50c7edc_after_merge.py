    def run(self):
        """ Add a new root (parent) directory to Medusa """

        self.location = unquote_plus(self.location)
        location_matched = False
        index = 0

        # disallow adding/setting an invalid dir
        if not os.path.isdir(self.location):
            return _responds(RESULT_FAILURE, msg='Location is invalid')

        root_dirs = []

        if not app.ROOT_DIRS:
            self.default = True
        else:
            index = int(app.ROOT_DIRS[0])
            # clean up the list: replace %xx escapes with single-character equivalent
            # and remove default_index value from list (this fixes the offset)
            root_dirs = [
                unquote_plus(directory)
                for directory in app.ROOT_DIRS[1:]
            ]
            for directory in root_dirs:
                if directory == self.location:
                    location_matched = True
                    if self.default:
                        index = root_dirs.index(self.location)
                    break

        if not location_matched:
            if self.default:
                root_dirs.insert(0, self.location)
            else:
                root_dirs.append(self.location)

        root_dirs_new = [
            unquote_plus(directory)
            for directory in root_dirs
        ]
        # reinsert index value in the list
        root_dirs_new.insert(0, index)
        app.ROOT_DIRS = root_dirs_new
        return _responds(RESULT_SUCCESS, _get_root_dirs(), msg='Root directories updated')