    def enter_dir(self, path, history=True):
        """Enter given path"""
        # TODO: Ensure that there is always a self.thisdir
        if path is None:
            return None
        path = str(path)

        # clear filter in the folder we're leaving
        if self.fm.settings.clear_filters_on_dir_change and self.thisdir:
            self.thisdir.filter = None
            self.thisdir.refilter()

        previous = self.thisdir

        # get the absolute path
        path = normpath(join(self.path, expanduser(path)))
        selectfile = None

        if not isdir(path):
            selectfile = path
            path = dirname(path)
        new_thisdir = self.fm.get_directory(path)

        try:
            os.chdir(path)
        except OSError:
            return True
        self.path = path
        self.thisdir = new_thisdir

        self.thisdir.load_content_if_outdated()

        # build the pathway, a tuple of directory objects which lie
        # on the path to the current directory.
        if path == '/':
            self.pathway = (self.fm.get_directory('/'), )
        else:
            pathway = []
            currentpath = '/'
            for comp in path.split('/'):
                currentpath = join(currentpath, comp)
                pathway.append(self.fm.get_directory(currentpath))
            self.pathway = tuple(pathway)

        self.assign_cursor_positions_for_subdirs()

        # set the current file.
        self.thisdir.sort_directories_first = self.fm.settings.sort_directories_first
        self.thisdir.sort_reverse = self.fm.settings.sort_reverse
        self.thisdir.sort_if_outdated()
        if selectfile:
            self.thisdir.move_to_obj(selectfile)
        if previous and previous.path != path:
            self.thisfile = self.thisdir.pointed_obj
        else:
            # This avoids setting self.pointer (through the 'move' signal) and
            # is required so that you can use enter_dir when switching tabs
            # without messing up the pointer.
            self._thisfile = self.thisdir.pointed_obj

        if history:
            self.history.add(new_thisdir)

        self.fm.signal_emit('cd', previous=previous, new=self.thisdir)

        return True