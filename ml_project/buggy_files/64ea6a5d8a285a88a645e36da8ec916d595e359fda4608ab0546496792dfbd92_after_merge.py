    def register_plugin(self):
        """Register plugin in Spyder's main window"""
        self.focus_changed.connect(self.main.plugin_focus_changed)
        self.main.add_dockwidget(self)
        # Connecting the following signal once the dockwidget has been created:
        self.shell.exception_occurred.connect(self.exception_occurred)