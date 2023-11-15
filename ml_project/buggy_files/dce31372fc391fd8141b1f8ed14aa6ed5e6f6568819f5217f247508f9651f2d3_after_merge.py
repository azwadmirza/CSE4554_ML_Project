    def run(self, edit):
        if self.view.settings().get("git_savvy.commit_on_close"):
            view_text = self.view.substr(sublime.Region(0, self.view.size()))
            help_text = self.view.settings().get("git_savvy.commit_view.help_text")
            message_txt = (view_text.split(help_text)[0]
                           if help_text in view_text
                           else "")
            message_txt = message_txt.strip()

            if message_txt:
                self.view.run_command("gs_commit_view_do_commit", {"message": message_txt})