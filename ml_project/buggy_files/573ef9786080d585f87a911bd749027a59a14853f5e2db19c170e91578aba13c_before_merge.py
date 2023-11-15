    def run(self):
        active_view_id = self.window.active_view().id()
        if active_view_id not in views_with_offer_made and sublime.ok_cancel_dialog(NO_REPO_MESSAGE):
            self.window.run_command("gs_init")
        else:
            views_with_offer_made.add(active_view_id)