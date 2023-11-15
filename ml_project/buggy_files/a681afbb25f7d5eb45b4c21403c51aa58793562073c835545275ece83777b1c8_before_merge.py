    def run(self, edit, message=None):
        sublime.set_timeout_async(lambda: self.run_async(commit_message=message), 0)