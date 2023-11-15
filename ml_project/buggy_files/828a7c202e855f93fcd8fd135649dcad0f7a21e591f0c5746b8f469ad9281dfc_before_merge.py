    def update_persistence(self, update=None):
        """Update :attr:`user_data`, :attr:`chat_data` and :attr:`bot_data` in :attr:`persistence`.

        Args:
            update (:class:`telegram.Update`, optional): The update to process. If passed, only the
            corresponding ``user_data`` and ``chat_data`` will be updated.
        """
        if self.persistence:
            chat_ids = self.chat_data.keys()
            user_ids = self.user_data.keys()

            if isinstance(update, Update):
                if update.effective_chat:
                    chat_ids = [update.effective_chat.id]
                else:
                    chat_ids = []
                if update.effective_user:
                    user_ids = [update.effective_user.id]
                else:
                    user_ids = []

            if self.persistence.store_bot_data:
                try:
                    self.persistence.update_bot_data(self.bot_data)
                except Exception as e:
                    try:
                        self.dispatch_error(update, e)
                    except Exception:
                        message = 'Saving bot data raised an error and an ' \
                                  'uncaught error was raised while handling ' \
                                  'the error with an error_handler'
                        self.logger.exception(message)
            if self.persistence.store_chat_data:
                for chat_id in chat_ids:
                    try:
                        self.persistence.update_chat_data(chat_id, self.chat_data[chat_id])
                    except Exception as e:
                        try:
                            self.dispatch_error(update, e)
                        except Exception:
                            message = 'Saving chat data raised an error and an ' \
                                      'uncaught error was raised while handling ' \
                                      'the error with an error_handler'
                            self.logger.exception(message)
            if self.persistence.store_user_data:
                for user_id in user_ids:
                    try:
                        self.persistence.update_user_data(user_id, self.user_data[user_id])
                    except Exception as e:
                        try:
                            self.dispatch_error(update, e)
                        except Exception:
                            message = 'Saving user data raised an error and an ' \
                                      'uncaught error was raised while handling ' \
                                      'the error with an error_handler'
                            self.logger.exception(message)