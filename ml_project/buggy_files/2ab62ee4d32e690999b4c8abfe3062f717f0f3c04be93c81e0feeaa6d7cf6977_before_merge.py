    def _add_callback_to_queue(self, request: CallbackRequest):
        self._callback_to_execute[request.full_filepath].append(request)
        # Callback has a higher priority over DAG Run scheduling
        if request.full_filepath in self._file_path_queue:
            self._file_path_queue.remove(request.full_filepath)
        self._file_path_queue.insert(0, request.full_filepath)