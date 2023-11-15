    def _convert_any_format(self):
        # convert book, and upload in case of google drive
        doLock = threading.Lock()
        doLock.acquire()
        index = self.current
        doLock.release()
        self.UIqueue[index]['stat'] = STAT_STARTED
        self.queue[index]['starttime'] = datetime.now()
        self.UIqueue[index]['formStarttime'] = self.queue[self.current]['starttime']
        curr_task = self.queue[index]['taskType']
        filename = self._convert_ebook_format()
        if filename:
            if config.config_use_google_drive:
                gdriveutils.updateGdriveCalibreFromLocal()
            if curr_task == TASK_CONVERT:
                self.add_email(self.queue[index]['settings']['subject'], self.queue[index]['path'],
                                filename, self.queue[index]['settings'], self.queue[index]['kindle'],
                                self.UIqueue[index]['user'], self.queue[index]['title'],
                                self.queue[index]['settings']['body'])