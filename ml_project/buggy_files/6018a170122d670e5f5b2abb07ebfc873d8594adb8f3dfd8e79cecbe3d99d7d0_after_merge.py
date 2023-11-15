    def __init__(self,
                 command,
                 callback,
                 filters=None,
                 allow_edited=None,
                 pass_args=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 run_async=False):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async)

        if isinstance(command, str):
            self.command = [command.lower()]
        else:
            self.command = [x.lower() for x in command]
        for comm in self.command:
            if not re.match(r'^[\da-z_]{1,32}$', comm):
                raise ValueError('Command is not a valid bot command')

        if filters:
            self.filters = Filters.update.messages & filters
        else:
            self.filters = Filters.update.messages

        if allow_edited is not None:
            warnings.warn('allow_edited is deprecated. See https://git.io/fxJuV for more info',
                          TelegramDeprecationWarning,
                          stacklevel=2)
            if not allow_edited:
                self.filters &= ~Filters.update.edited_message
        self.pass_args = pass_args