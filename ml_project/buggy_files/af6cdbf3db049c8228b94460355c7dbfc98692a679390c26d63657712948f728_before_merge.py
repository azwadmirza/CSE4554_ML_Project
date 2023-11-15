    def _prompt_continue(self):
        """ Show uncommitted changes, and ask if user wants to continue. """

        changes = subprocess.check_output(['git', 'status', '--porcelain'])
        if changes.strip():
            changes = subprocess.check_output(['git', 'status']).strip()
            message = (
                "You have the following changes:\n%s\n\n"
                "Anything not committed, and unknown to Nikola may be lost, "
                "or committed onto the wrong branch. Do you wish to continue?"
            ) % changes
            proceed = ask_yesno(message, False)
        else:
            proceed = True

        return proceed