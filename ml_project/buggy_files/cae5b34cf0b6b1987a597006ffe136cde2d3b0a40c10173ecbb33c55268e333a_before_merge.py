    def do_clone(self):
        sublime.status_message("Start cloning {}".format(self.git_url))
        self.git("clone", self.git_url, self.suggested_git_root)
        sublime.status_message("Cloned repo successfully.")
        self.open_folder()
        util.view.refresh_gitsavvy(self.window.active_view())