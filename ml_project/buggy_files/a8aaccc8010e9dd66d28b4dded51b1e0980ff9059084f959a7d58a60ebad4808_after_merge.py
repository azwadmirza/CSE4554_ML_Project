    def _handleError(self, error_message):
        web.app.logger.error(error_message)
        self.UIqueue[self.current]['stat'] = STAT_FAIL
        self.UIqueue[self.current]['progress'] = "100 %"
        self.UIqueue[self.current]['formRuntime'] = datetime.now() - self.queue[self.current]['starttime']
        self.UIqueue[self.current]['message'] = error_message