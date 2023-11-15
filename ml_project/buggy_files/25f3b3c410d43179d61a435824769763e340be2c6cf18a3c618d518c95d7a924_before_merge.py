    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.main.add_dockwidget(self)
        self.main.console.set_help(self)

        self.internal_shell = self.main.console.shell
        self.console = self.main.console
        self.ipyconsole = self.main.ipyconsole
        self.editor = self.main.editor