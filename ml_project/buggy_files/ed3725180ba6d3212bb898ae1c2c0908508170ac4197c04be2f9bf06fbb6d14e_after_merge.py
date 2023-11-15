    def _trigger_timeout(self, context, job=None):
        self.logger.debug('conversation timeout was triggered!')
        
        # Backward compatibility with bots that do not use CallbackContext
        if isinstance(context, CallbackContext):
            context = context.job.context
        else:
            context = job.context
        
        del self.timeout_jobs[context.conversation_key]
        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(context.update)
            if check is not None and check is not False:
                handler.handle_update(context.update, context.dispatcher, check)
        self.update_state(self.END, context.conversation_key)