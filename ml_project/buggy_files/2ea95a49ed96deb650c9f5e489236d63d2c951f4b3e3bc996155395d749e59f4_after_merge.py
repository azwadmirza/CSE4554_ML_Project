    def run_async(self, commit_message=None):
        if commit_message is None:
            view_text = self.view.substr(sublime.Region(0, self.view.size()))
            help_text = self.view.settings().get("git_savvy.commit_view.help_text")
            commit_message = view_text.split(help_text)[0]

        include_unstaged = self.view.settings().get("git_savvy.commit_view.include_unstaged")

        show_panel_overrides = \
            sublime.load_settings("GitSavvy.sublime-settings").get("show_panel_for")

        self.git(
            "commit",
            "-q" if "commit" not in show_panel_overrides else None,
            "-a" if include_unstaged else None,
            "--amend" if self.view.settings().get("git_savvy.commit_view.amend") else None,
            "-F",
            "-",
            stdin=commit_message
        )

        is_commit_view = self.view.settings().get("git_savvy.commit_view")
        if is_commit_view and not self.commit_on_close:
            self.view.window().focus_view(self.view)
            self.view.set_scratch(True)  # ignore dirty on actual commit
            self.view.window().run_command("close_file")

        sublime.set_timeout_async(
            lambda: util.view.refresh_gitsavvy(sublime.active_window().active_view()))