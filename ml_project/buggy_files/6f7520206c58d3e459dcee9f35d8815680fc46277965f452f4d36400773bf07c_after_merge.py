    def __init__(self,
                 filters,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 message_updates=None,
                 channel_post_updates=None,
                 edited_updates=None,
                 run_async=False):

        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async)
        if message_updates is False and channel_post_updates is False and edited_updates is False:
            raise ValueError(
                'message_updates, channel_post_updates and edited_updates are all False')
        if filters is not None:
            self.filters = Filters.update & filters
        else:
            self.filters = Filters.update
        if message_updates is not None:
            warnings.warn('message_updates is deprecated. See https://git.io/fxJuV for more info',
                          TelegramDeprecationWarning,
                          stacklevel=2)
            if message_updates is False:
                self.filters &= ~Filters.update.message

        if channel_post_updates is not None:
            warnings.warn('channel_post_updates is deprecated. See https://git.io/fxJuV '
                          'for more info',
                          TelegramDeprecationWarning,
                          stacklevel=2)
            if channel_post_updates is False:
                self.filters &= ~Filters.update.channel_post

        if edited_updates is not None:
            warnings.warn('edited_updates is deprecated. See https://git.io/fxJuV for more info',
                          TelegramDeprecationWarning,
                          stacklevel=2)
            if edited_updates is False:
                self.filters &= ~(Filters.update.edited_message
                                  | Filters.update.edited_channel_post)