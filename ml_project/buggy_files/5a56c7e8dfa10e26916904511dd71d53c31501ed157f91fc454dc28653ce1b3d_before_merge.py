    def _handleSuccess(self):
        self.UIqueue[self.current]['stat'] = STAT_FINISH_SUCCESS
        self.UIqueue[self.current]['progress'] = "100 %"
        self.UIqueue[self.current]['runtime'] = self._formatRuntime(
            datetime.now() - self.queue[self.current]['starttime'])