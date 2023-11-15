    def run(self):
        main_thread = _get_main_thread()
        while main_thread.is_alive():
            doLock = threading.Lock()
            doLock.acquire()
            if self.current != self.last:
                index = self.current
                doLock.release()
                if self.queue[index]['taskType'] == TASK_EMAIL:
                    self._send_raw_email()
                if self.queue[index]['taskType'] == TASK_CONVERT:
                    self._convert_any_format()
                if self.queue[index]['taskType'] == TASK_CONVERT_ANY:
                    self._convert_any_format()
                # TASK_UPLOAD is handled implicitly
                doLock.acquire()
                self.current += 1
                doLock.release()
            else:
                doLock.release()
            if main_thread.is_alive():
                time.sleep(1)