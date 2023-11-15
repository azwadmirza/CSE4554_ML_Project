    def report_record_done(self, count, err_msg=""):
        """
        Report the number of records in the latest processed batch,
        so TaskDataService knows if some pending tasks are finished
        and report_task_result to the master.
        Return True if there are some finished tasks, False otherwise.
        """
        self._reported_record_count += count
        if err_msg:
            self._failed_record_count += count

        task = self._pending_tasks[0]
        total_record_num = task.end - task.start
        if self._reported_record_count >= total_record_num:
            if err_msg:
                self._log_fail_records(task, err_msg)

            # Keep popping tasks until the reported record count is less
            # than the size of the current data since `batch_size` may be
            # larger than `task.end - task.start`
            with self._lock:
                while self._pending_tasks and self._reported_record_count >= (
                    self._pending_tasks[0].end - self._pending_tasks[0].start
                ):
                    task = self._pending_tasks[0]
                    self._reported_record_count -= task.end - task.start
                    self._pending_tasks.popleft()
                    self._do_report_task(task, err_msg)
                    self._failed_record_count = 0
                if self._pending_tasks:
                    self._current_task = self._pending_tasks[0]
            return True
        return False