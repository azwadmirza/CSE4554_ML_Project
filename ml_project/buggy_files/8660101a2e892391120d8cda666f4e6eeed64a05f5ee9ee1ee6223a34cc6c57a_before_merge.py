    def get_taskstatus(self):
        if self.current  < len(self.queue):
            if self.UIqueue[self.current]['stat'] == STAT_STARTED:
                if self.queue[self.current]['taskType'] == TASK_EMAIL:
                    self.UIqueue[self.current]['progress'] = self.get_send_status()
                self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                        datetime.now() - self.queue[self.current]['starttime'])
        return self.UIqueue