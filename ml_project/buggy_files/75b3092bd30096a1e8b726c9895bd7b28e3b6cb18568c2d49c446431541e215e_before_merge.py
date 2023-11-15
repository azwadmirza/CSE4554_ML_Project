    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.editor = self.main.editor
        self.workingdirectory = self.main.workingdirectory

        self.main.pythonpath_changed()
        self.main.restore_scrollbar_position.connect(
                                               self.restore_scrollbar_position)
        self.pythonpath_changed.connect(self.main.pythonpath_changed)
        self.create_module.connect(self.editor.new)
        self.edit.connect(self.editor.load)
        self.removed.connect(self.editor.removed)
        self.removed_tree.connect(self.editor.removed_tree)
        self.renamed.connect(self.editor.renamed)
        self.editor.set_projects(self)
        self.main.add_dockwidget(self)

        self.sig_open_file.connect(self.main.open_file)

        # New project connections. Order matters!
        self.sig_project_loaded.connect(
            lambda v: self.workingdirectory.chdir(v))
        self.sig_project_loaded.connect(
            lambda v: self.main.update_window_title())
        self.sig_project_loaded.connect(
            lambda v: self.editor.setup_open_files())
        self.sig_project_loaded.connect(self.update_explorer)
        self.sig_project_closed[object].connect(
            lambda v: self.workingdirectory.chdir(self.get_last_working_dir()))
        self.sig_project_closed.connect(
            lambda v: self.main.update_window_title())
        self.sig_project_closed.connect(
            lambda v: self.editor.setup_open_files())
        self.recent_project_menu.aboutToShow.connect(self.setup_menu_actions)