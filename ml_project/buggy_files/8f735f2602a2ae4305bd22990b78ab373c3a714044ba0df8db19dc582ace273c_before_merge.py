    def run(self):
        """ Delete a root (parent) directory from Medusa """
        if app.ROOT_DIRS == '':
            return _responds(RESULT_FAILURE, _get_root_dirs(), msg='No root directories detected')

        new_index = 0
        root_dirs_new = []
        root_dirs = app.ROOT_DIRS
        index = int(root_dirs[0])
        root_dirs.pop(0)
        # clean up the list - replace %xx escapes by their single-character equivalent
        root_dirs = [unquote_plus(x) for x in root_dirs]
        old_root_dir = root_dirs[index]
        for curRootDir in root_dirs:
            if not curRootDir == self.location:
                root_dirs_new.append(curRootDir)
            else:
                new_index = 0

        for curIndex, curNewRootDir in enumerate(root_dirs_new):
            if curNewRootDir is old_root_dir:
                new_index = curIndex
                break

        root_dirs_new = [unquote_plus(x) for x in root_dirs_new]
        if root_dirs_new:
            root_dirs_new.insert(0, new_index)
        root_dirs_new = '|'.join(text_type(x) for x in root_dirs_new)

        app.ROOT_DIRS = root_dirs_new
        # what if the root dir was not found?
        return _responds(RESULT_SUCCESS, _get_root_dirs(), msg='Root directory deleted')