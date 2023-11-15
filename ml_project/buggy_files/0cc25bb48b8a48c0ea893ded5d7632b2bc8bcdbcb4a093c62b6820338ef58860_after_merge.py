    def start_new_processes(self):
        """Start more processors if we have enough slots and files to process"""
        while self._parallelism - len(self._processors) > 0 and self._file_path_queue:
            file_path = self._file_path_queue.pop(0)
            # Stop creating duplicate processor i.e. processor with the same filepath
            if file_path in self._processors.keys():
                continue

            callback_to_execute_for_file = self._callback_to_execute[file_path]
            processor = self._processor_factory(
                file_path, callback_to_execute_for_file, self._dag_ids, self._pickle_dags
            )

            del self._callback_to_execute[file_path]
            Stats.incr('dag_processing.processes')

            processor.start()
            self.log.debug("Started a process (PID: %s) to generate tasks for %s", processor.pid, file_path)
            self._processors[file_path] = processor
            self.waitables[processor.waitable_handle] = processor