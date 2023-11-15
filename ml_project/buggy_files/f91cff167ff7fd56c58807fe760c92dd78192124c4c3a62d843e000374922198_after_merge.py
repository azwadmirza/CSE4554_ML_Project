    def __init__(self,
                 pattern,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 allow_edited=False,
                 message_updates=True,
                 channel_post_updates=False,
                 edited_updates=False,
                 run_async=False):
        warnings.warn('RegexHandler is deprecated. See https://git.io/fxJuV for more info',
                      TelegramDeprecationWarning,
                      stacklevel=2)
        super().__init__(Filters.regex(pattern),
                         callback,
                         pass_update_queue=pass_update_queue,
                         pass_job_queue=pass_job_queue,
                         pass_user_data=pass_user_data,
                         pass_chat_data=pass_chat_data,
                         message_updates=message_updates,
                         channel_post_updates=channel_post_updates,
                         edited_updates=edited_updates,
                         run_async=run_async)
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict