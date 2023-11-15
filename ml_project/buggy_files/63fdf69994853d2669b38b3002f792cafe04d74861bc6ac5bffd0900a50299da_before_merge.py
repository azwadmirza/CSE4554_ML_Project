    def _convert_any_format(self):
        # convert book, and upload in case of google drive
        self.UIqueue[self.current]['stat'] = STAT_STARTED
        self.queue[self.current]['starttime'] = datetime.now()
        self.UIqueue[self.current]['formStarttime'] = self.queue[self.current]['starttime']
        curr_task = self.queue[self.current]['taskType']
        filename = self._convert_ebook_format()
        if filename:
            if config.config_use_google_drive:
                gdriveutils.updateGdriveCalibreFromLocal()
            if curr_task == TASK_CONVERT:
                self.add_email(self.queue[self.current]['settings']['subject'], self.queue[self.current]['path'],
                                filename, self.queue[self.current]['settings'], self.queue[self.current]['kindle'],
                                self.UIqueue[self.current]['user'], self.queue[self.current]['title'],
                                self.queue[self.current]['settings']['body'])