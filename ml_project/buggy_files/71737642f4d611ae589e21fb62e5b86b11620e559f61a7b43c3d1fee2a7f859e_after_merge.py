    def _handleSuccess(self):
        self.doLock.acquire()
        index = self.current
        self.doLock.release()
        self.UIqueue[index]['stat'] = STAT_FINISH_SUCCESS
        self.UIqueue[index]['progress'] = "100 %"
        self.UIqueue[index]['formRuntime'] = datetime.now() - self.queue[self.current]['starttime']