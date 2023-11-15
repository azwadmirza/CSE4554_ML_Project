    def tab_close_prompt_if_pinned(self, tab, force, yes_action):
        """Helper method for tab_close.

        If tab is pinned, prompt. If not, run yes_action.
        If tab is destroyed, abort question.
        """
        if tab.data.pinned and not force:
            message.confirm_async(
                title='Pinned Tab',
                text="Are you sure you want to close a pinned tab?",
                yes_action=yes_action, default=False, abort_on=[tab.destroyed])
        else:
            yes_action()