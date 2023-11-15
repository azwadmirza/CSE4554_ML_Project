    def _add_callback_to_queue(self, request: CallbackRequest):
        self._callback_to_execute[request.full_filepath].append(request)
        # Callback has a higher priority over DAG Run scheduling
        if request.full_filepath in self._file_path_queue:
            # Remove file paths matching request.full_filepath from self._file_path_queue
            # Since we are already going to use that filepath to run callback,
            # there is no need to have same file path again in the queue
            self._file_path_queue = [
                file_path for file_path in self._file_path_queue if file_path != request.full_filepath
            ]
        self._file_path_queue.insert(0, request.full_filepath)