    def run_async(self):
        log, cursor = self.interface.get_log()
        if log is None or cursor is None or cursor == len(log) - 1:
            return

        branch_name, ref = self.interface.get_branch_state()

        undone_action = log[cursor+1]
        if undone_action["branch_name"] != branch_name:
            sublime.error_message("Current branch does not match expected. Cannot redo.")
            return

        try:
            self.checkout_ref(undone_action["ref_after"])
            self.git("branch", "-f", branch_name, "HEAD")
            cursor += 1

        except Exception as e:
            sublime.error_message("Error encountered. Cannot redo.")
            raise e

        finally:
            self.checkout_ref(branch_name)
            self.interface.set_log(log, cursor)
            util.view.refresh_gitsavvy(self.view)