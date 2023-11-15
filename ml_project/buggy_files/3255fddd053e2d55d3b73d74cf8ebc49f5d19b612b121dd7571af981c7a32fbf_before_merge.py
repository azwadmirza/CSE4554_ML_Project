    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):
        meta = self._get_result_meta(result=result, state=state,
                                     traceback=traceback, request=request)
        meta['task_id'] = bytes_to_str(task_id)

        # Retrieve metadata from the backend, if the status
        # is a success then we ignore any following update to the state.
        # This solves a task deduplication issue because of network
        # partitioning or lost workers. This issue involved a race condition
        # making a lost task overwrite the last successful result in the
        # result backend.
        current_meta = self._get_task_meta_for(task_id)

        if current_meta['status'] == states.SUCCESS:
            return result

        self.set(self.get_key_for_task(task_id), self.encode(meta), state)
        return result