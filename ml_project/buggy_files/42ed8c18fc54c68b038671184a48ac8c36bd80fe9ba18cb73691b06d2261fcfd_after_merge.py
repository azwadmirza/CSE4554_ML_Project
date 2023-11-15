    def change_mode(self, mode):
        """
        Given the name of a mode, will make the necessary changes to put the
        editor into the new mode.
        """
        # Remove the old mode's REPL / filesystem / plotter if required.
        old_mode = self.modes[self.mode]
        if hasattr(old_mode, "remove_repl"):
            old_mode.remove_repl()
        if hasattr(old_mode, "remove_fs"):
            old_mode.remove_fs()
        if hasattr(old_mode, "remove_plotter"):
            if old_mode.plotter:
                old_mode.remove_plotter()
        # Deactivate old mode
        self.modes[self.mode].deactivate()
        # Re-assign to new mode.
        self.mode = mode
        # Activate new mode
        self.modes[mode].activate()
        # Update buttons.
        self._view.change_mode(self.modes[mode])
        button_bar = self._view.button_bar
        button_bar.connect("modes", self.select_mode, "Ctrl+Shift+M")
        button_bar.connect("new", self.new, "Ctrl+N")
        button_bar.connect("load", self.load, "Ctrl+O")
        button_bar.connect("save", self.save, "Ctrl+S")
        for action in self.modes[mode].actions():
            button_bar.connect(
                action["name"], action["handler"], action["shortcut"]
            )
        button_bar.connect("zoom-in", self.zoom_in, "Ctrl++")
        button_bar.connect("zoom-out", self.zoom_out, "Ctrl+-")
        button_bar.connect("theme", self.toggle_theme, "F1")
        button_bar.connect("check", self.check_code, "F2")
        if sys.version_info[:2] >= (3, 6):
            button_bar.connect("tidy", self.tidy_code, "F10")
        button_bar.connect("help", self.show_help, "Ctrl+H")
        button_bar.connect("quit", self.quit, "Ctrl+Q")
        self._view.status_bar.set_mode(self.modes[mode].name)
        # Update references to default file locations.
        try:
            workspace_dir = self.modes[mode].workspace_dir()
            logger.info("Workspace directory: {}".format(workspace_dir))
        except Exception as e:
            # Avoid crashing if workspace_dir raises, use default path instead
            workspace_dir = self.modes["python"].workspace_dir()
            logger.error(
                (
                    "Could not open {} mode workspace directory, "
                    'due to exception "{}".'
                    "Using:\n\n{}\n\n...to store your code instead"
                ).format(mode, repr(e), workspace_dir)
            )
        # Reset remembered current path for load/save dialogs.
        self.current_path = ""
        # Ensure auto-save timeouts are set.
        if self.modes[mode].save_timeout > 0:
            # Start the timer
            self._view.set_timer(self.modes[mode].save_timeout, self.autosave)
        else:
            # Stop the timer
            self._view.stop_timer()
        # Update breakpoint states.
        if not (self.modes[mode].is_debugger or self.modes[mode].has_debugger):
            for tab in self._view.widgets:
                tab.breakpoint_handles = set()
                tab.reset_annotations()
        self.show_status_message(
            _("Changed to {} mode.").format(self.modes[mode].name)
        )