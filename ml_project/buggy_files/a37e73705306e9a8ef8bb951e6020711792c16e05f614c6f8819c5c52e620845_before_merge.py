    def __init__(self,
                 prefix,
                 command,
                 callback,
                 filters=None,
                 pass_args=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):

        self._prefix = list()
        self._command = list()
        self._commands = list()

        super().__init__(
            'nocommand', callback, filters=filters, allow_edited=None, pass_args=pass_args,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

        self.prefix = prefix
        self.command = command
        self._build_commands()