    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.add_dockwidget()

        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.edit_goto.connect(self.main.editor.load)
        self.edit_goto[str, int, str, bool].connect(
                         lambda fname, lineno, word, processevents:
                         self.main.editor.load(fname, lineno, word,
                                               processevents=processevents))
        self.main.editor.breakpoints_saved.connect(self.set_spyder_breakpoints)
        self.main.editor.run_in_current_ipyclient.connect(self.run_script)
        self.main.editor.run_cell_in_ipyclient.connect(self.run_cell)
        self.main.editor.debug_cell_in_ipyclient.connect(self.debug_cell)
        self.main.workingdirectory.set_current_console_wd.connect(
            self.set_current_client_working_directory)
        self.tabwidget.currentChanged.connect(self.update_working_directory)
        self._remove_old_stderr_files()