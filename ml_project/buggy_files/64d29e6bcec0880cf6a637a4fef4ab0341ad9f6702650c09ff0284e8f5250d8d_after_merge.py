    def console(self, console):
        self._console = console
        self.dockConsole.widget = console
        self._update_palette()