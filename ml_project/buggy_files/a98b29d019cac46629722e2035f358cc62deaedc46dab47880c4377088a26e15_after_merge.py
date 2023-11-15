    def savvy_settings(self):
        if not self._savvy_settings:
            window = (
                maybe(lambda: self.window)  # type: ignore[attr-defined]
                or maybe(lambda: self.view.window())  # type: ignore[attr-defined]
                or sublime.active_window()
            )
            self._savvy_settings = GitSavvySettings(window)
        return self._savvy_settings