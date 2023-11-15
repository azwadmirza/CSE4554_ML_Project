    def get(self, key, default=None):
        window = sublime.active_window()
        view = window.active_view()
        project_savvy_settings = view.settings().get("GitSavvy", {}) or {}

        if key in project_savvy_settings:
            return project_savvy_settings[key]

        # fall back to old style project setting
        project_data = window.project_data()
        if project_data and "GitSavvy" in project_data:
            project_savvy_settings = project_data["GitSavvy"]
            if key in project_savvy_settings:
                return project_savvy_settings.get(key)

        return self.global_settings.get(key, default)