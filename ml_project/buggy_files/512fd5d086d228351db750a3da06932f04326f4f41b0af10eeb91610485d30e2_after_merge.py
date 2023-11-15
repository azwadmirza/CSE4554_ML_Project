    def run_async(self):
        log, cursor = self.interface.get_log()
        if log is None or cursor is None or cursor == -1:
            return

        branch_name, ref, _ = self.interface.get_branch_state()

        current = log[cursor]
        if current["branch_name"] != branch_name:
            sublime.error_message("Current branch does not match expected. Cannot undo.")
            return

        try:
            self.checkout_ref(current["ref_before"])
            self.git("branch", "-f", branch_name, "HEAD")
            cursor -= 1

        except Exception as e:
            sublime.error_message("Error encountered. Cannot undo.")
            raise e

        finally:
            self.checkout_ref(branch_name)
            self.interface.set_log(log, cursor)
            util.view.refresh_gitsavvy(self.view)