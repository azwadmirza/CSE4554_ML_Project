    def _handleError(self, error_message):
        log.error(error_message)
        doLock = threading.Lock()
        doLock.acquire()
        index = self.current
        doLock.release()
        self.UIqueue[index]['stat'] = STAT_FAIL
        self.UIqueue[index]['progress'] = "100 %"
        self.UIqueue[index]['formRuntime'] = datetime.now() - self.queue[self.current]['starttime']
        self.UIqueue[index]['message'] = error_message