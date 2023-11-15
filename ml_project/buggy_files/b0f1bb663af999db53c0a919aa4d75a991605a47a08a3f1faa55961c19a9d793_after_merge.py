    def _get_starting_path_list(self):
        path = self.environ.get('PATH', '')
        if on_win:
            # On Windows, the Anaconda Python interpreter prepends sys.prefix\Library\bin on
            # startup. It's a hack that allows users to avoid using the correct activation
            # procedure; a hack that needs to go away because it doesn't add all the paths.
            # See: https://github.com/AnacondaRecipes/python-feedstock/blob/master/recipe/0005-Win32-Ensure-Library-bin-is-in-os.environ-PATH.patch  # NOQA
            # But, we now detect if that has happened because:
            #   1. In future we would like to remove this hack and require real activation.
            #   2. We should not assume that the Anaconda Python interpreter is being used.
            path_split = path.split(os.pathsep)
            library_bin = r"%s\Library\bin" % (sys.prefix)
            # ^^^ deliberately the same as: https://github.com/AnacondaRecipes/python-feedstock/blob/8e8aee4e2f4141ecfab082776a00b374c62bb6d6/recipe/0005-Win32-Ensure-Library-bin-is-in-os.environ-PATH.patch#L20  # NOQA
            if paths_equal(path_split[0], library_bin):
                return path_split[1:]
            else:
                return path_split
        else:
            return path.split(os.pathsep)