    def _trigger_timeout(self, bot, job):
        self.logger.debug('conversation timeout was triggered!')
        del self.timeout_jobs[job.context.conversation_key]
        handlers = self.states.get(self.TIMEOUT, [])
        for handler in handlers:
            check = handler.check_update(job.context.update)
            if check is not None and check is not False:
                handler.handle_update(job.context.update, job.context.dispatcher, check)
        self.update_state(self.END, job.context.conversation_key)