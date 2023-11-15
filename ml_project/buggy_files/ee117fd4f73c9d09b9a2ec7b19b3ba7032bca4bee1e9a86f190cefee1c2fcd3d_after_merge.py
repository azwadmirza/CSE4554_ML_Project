    def get_taskstatus(self):
        doLock = threading.Lock()
        doLock.acquire()
        if self.current  < len(self.queue):
            if self.UIqueue[self.current]['stat'] == STAT_STARTED:
                if self.queue[self.current]['taskType'] == TASK_EMAIL:
                    self.UIqueue[self.current]['progress'] = self.get_send_status()
                self.UIqueue[self.current]['formRuntime'] = datetime.now() - self.queue[self.current]['starttime']
                self.UIqueue[self.current]['rt'] = self.UIqueue[self.current]['formRuntime'].days*24*60 \
                                                   + self.UIqueue[self.current]['formRuntime'].seconds \
                                                   + self.UIqueue[self.current]['formRuntime'].microseconds
        doLock.release()
        return self.UIqueue