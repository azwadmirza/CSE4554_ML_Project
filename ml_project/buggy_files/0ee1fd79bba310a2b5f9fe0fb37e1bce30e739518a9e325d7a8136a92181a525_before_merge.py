    def open_project(self, path=None, restart_consoles=True,
                     save_previous_files=True):
        """Open the project located in `path`"""
        self.notify_project_open(path)
        self.unmaximize()
        if path is None:
            basedir = get_home_dir()
            path = getexistingdirectory(parent=self,
                                        caption=_("Open project"),
                                        basedir=basedir)
            path = encoding.to_unicode_from_fs(path)
            if not self.is_valid_project(path):
                if path:
                    QMessageBox.critical(self, _('Error'),
                                _("<b>%s</b> is not a Spyder project!") % path)
                return
        else:
            path = encoding.to_unicode_from_fs(path)

        self.add_to_recent(path)

        # A project was not open before
        if self.current_active_project is None:
            if save_previous_files and self.main.editor is not None:
                self.main.editor.save_open_files()
            if self.main.editor is not None:
                self.main.editor.set_option('last_working_dir',
                                            getcwd_or_home())
            if self.get_option('visible_if_project_open'):
                self.show_explorer()
        else:
            # We are switching projects
            if self.main.editor is not None:
                self.set_project_filenames(
                    self.main.editor.get_open_filenames())

            # TODO: Don't emit sig_project_closed when we support
            # multiple workspaces.
            self.sig_project_closed.emit(
                self.current_active_project.root_path)

        project = EmptyProject(path)
        self.current_active_project = project
        self.latest_project = project
        self.set_option('current_project_path', self.get_active_project_path())

        self.setup_menu_actions()
        self.sig_project_loaded.emit(path)
        self.sig_pythonpath_changed.emit()
        self.watcher.start(path)

        if restart_consoles:
            self.restart_consoles()