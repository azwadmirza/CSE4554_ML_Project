        def process_response(task):
            try:
                response = task.result()
            except Exception as e:
                self._loop_create_task(
                    self.errors_handlers.notify(types.Update.get_current(), e))
            else:
                if isinstance(response, BaseResponse):
                    self._loop_create_task(response.execute_response(self.bot))