    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        ipyconsole = self.main.ipyconsole
        treewidget = self.explorer.treewidget
        lspmgr = self.main.completions

        self.add_dockwidget()
        self.explorer.sig_open_file.connect(self.main.open_file)
        self.register_widget_shortcuts(treewidget)

        treewidget.sig_delete_project.connect(self.delete_project)
        treewidget.sig_edit.connect(self.main.editor.load)
        treewidget.sig_removed.connect(self.main.editor.removed)
        treewidget.sig_removed_tree.connect(self.main.editor.removed_tree)
        treewidget.sig_renamed.connect(self.main.editor.renamed)
        treewidget.sig_renamed_tree.connect(self.main.editor.renamed_tree)
        treewidget.sig_create_module.connect(self.main.editor.new)
        treewidget.sig_new_file.connect(
            lambda t: self.main.editor.new(text=t))
        treewidget.sig_open_interpreter.connect(
            ipyconsole.create_client_from_path)
        treewidget.redirect_stdio.connect(
            self.main.redirect_internalshell_stdio)
        treewidget.sig_run.connect(
            lambda fname:
            ipyconsole.run_script(fname, osp.dirname(fname), '', False, False,
                                  False, True, False))

        # New project connections. Order matters!
        self.sig_project_loaded.connect(
            lambda v: self.main.workingdirectory.chdir(v))
        self.sig_project_loaded.connect(
            lambda v: self.main.set_window_title())
        self.sig_project_loaded.connect(
            functools.partial(lspmgr.project_path_update,
                              update_kind='addition'))
        self.sig_project_loaded.connect(
            lambda v: self.main.editor.setup_open_files())
        self.sig_project_loaded.connect(self.update_explorer)
        self.sig_project_closed[object].connect(
            lambda v: self.main.workingdirectory.chdir(
                self.get_last_working_dir()))
        self.sig_project_closed.connect(
            lambda v: self.main.set_window_title())
        self.sig_project_closed.connect(
            functools.partial(lspmgr.project_path_update,
                              update_kind='deletion'))
        self.sig_project_closed.connect(
            lambda v: self.main.editor.setup_open_files())
        self.recent_project_menu.aboutToShow.connect(self.setup_menu_actions)

        self.main.pythonpath_changed()
        self.main.restore_scrollbar_position.connect(
                                               self.restore_scrollbar_position)
        self.sig_pythonpath_changed.connect(self.main.pythonpath_changed)
        self.main.editor.set_projects(self)

        # Connect to file explorer to keep single click to open files in sync
        self.main.explorer.fileexplorer.sig_option_changed.connect(
            self.set_single_click_to_open
        )