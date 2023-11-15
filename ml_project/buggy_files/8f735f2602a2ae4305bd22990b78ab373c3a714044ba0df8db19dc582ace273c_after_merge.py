    def run(self):
        """ Delete a root (parent) directory from Medusa """
        if not app.ROOT_DIRS:
            return _responds(RESULT_FAILURE, _get_root_dirs(), msg='No root directories detected')

        index = int(app.ROOT_DIRS[0])
        # clean up the list: replace %xx escapes with single-character equivalent
        # and remove default_index value from list (this fixes the offset)
        root_dirs = [
            unquote_plus(directory)
            for directory in app.ROOT_DIRS[1:]
        ]
        default_dir = root_dirs[index]
        location = unquote_plus(self.location)
        try:
            root_dirs.remove(location)
        except ValueError:
            result = RESULT_FAILURE
            msg = 'Location not in root directories'
            return _responds(result, _get_root_dirs(), msg=msg)

        try:
            index = root_dirs.index(default_dir)
        except ValueError:
            if default_dir == location:
                result = RESULT_DENIED
                msg = 'Default directory cannot be deleted; Please set a new default directory.'
            else:
                result = RESULT_ERROR
                msg = 'Default directory not found'
        else:
            root_dirs.insert(0, index)
            app.ROOT_DIRS = root_dirs
            result = RESULT_SUCCESS
            msg = 'Root directory {0} deleted'.format(location)

        return _responds(result, _get_root_dirs(), msg=msg)