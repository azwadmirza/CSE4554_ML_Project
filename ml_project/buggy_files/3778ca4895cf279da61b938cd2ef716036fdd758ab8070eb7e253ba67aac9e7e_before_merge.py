    def __init__(self,
                 sync_up_template,
                 sync_down_template,
                 delete_template=noop_template):
        """Syncs between two directories with the given command.

        Arguments:
            sync_up_template (str): A runnable string template; needs to
                include replacement fields '{source}' and '{target}'.
            sync_down_template (str): A runnable string template; needs to
                include replacement fields '{source}' and '{target}'.
            delete_template (Optional[str]): A runnable string template; needs
                to include replacement field '{target}'. Noop by default.
        """
        self._validate_sync_string(sync_up_template)
        self._validate_sync_string(sync_down_template)
        self.sync_up_template = sync_up_template
        self.sync_down_template = sync_down_template
        self.delete_template = delete_template
        self.logfile = None
        self.cmd_process = None