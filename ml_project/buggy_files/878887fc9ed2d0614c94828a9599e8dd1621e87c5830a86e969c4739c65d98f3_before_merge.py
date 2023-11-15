    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        ipyconsole = self.main.ipyconsole
        treewidget = self.fileexplorer.treewidget

        self.add_dockwidget()
        self.fileexplorer.sig_open_file.connect(self.main.open_file)
        self.register_widget_shortcuts(treewidget)

        treewidget.sig_edit.connect(self.main.editor.load)
        treewidget.sig_removed.connect(self.main.editor.removed)
        treewidget.sig_removed_tree.connect(self.main.editor.removed_tree)
        treewidget.sig_renamed.connect(self.main.editor.renamed)
        treewidget.sig_renamed_tree.connect(self.main.editor.renamed_tree)
        treewidget.sig_create_module.connect(self.main.editor.new)
        treewidget.sig_new_file.connect(lambda t: self.main.editor.new(text=t))
        treewidget.sig_open_interpreter.connect(
            ipyconsole.create_client_from_path)
        treewidget.redirect_stdio.connect(
            self.main.redirect_internalshell_stdio)
        treewidget.sig_run.connect(
            lambda fname:
            ipyconsole.run_script(fname, osp.dirname(fname), '', False, False,
                                  False, True))
        treewidget.sig_open_dir.connect(
            lambda dirname:
            self.main.workingdirectory.chdir(dirname,
                                             refresh_explorer=False,
                                             refresh_console=True))

        self.main.editor.open_dir.connect(self.chdir)

        # Signal "set_explorer_cwd(QString)" will refresh only the
        # contents of path passed by the signal in explorer:
        self.main.workingdirectory.set_explorer_cwd.connect(
                     lambda directory: self.refresh_plugin(new_path=directory,
                                                           force_current=True))