    def tab_close_prompt_if_pinned(self, tab, force, yes_action):
        """Helper method for tab_close.

        If tab is pinned, prompt. If everything is good, run yes_action.
        """
        if tab.data.pinned and not force:
            message.confirm_async(
                title='Pinned Tab',
                text="Are you sure you want to close a pinned tab?",
                yes_action=yes_action, default=False)
        else:
            yes_action()