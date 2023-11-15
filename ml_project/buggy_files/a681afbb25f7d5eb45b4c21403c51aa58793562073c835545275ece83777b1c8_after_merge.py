    def run(self, edit, message=None):
        self.commit_on_close = self.view.settings().get("git_savvy.commit_on_close")
        if self.commit_on_close:
            # make sure the view would not be closed by commiting synchronously
            self.run_async(commit_message=message)
        else:
            sublime.set_timeout_async(lambda: self.run_async(commit_message=message), 0)