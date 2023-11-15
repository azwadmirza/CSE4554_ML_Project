        def process_response(task):
            try:
                response = task.result()
            except Exception as e:
                self.loop.create_task(
                    self.errors_handlers.notify(types.Update.get_current(), e))
            else:
                if isinstance(response, BaseResponse):
                    self.loop.create_task(response.execute_response(self.bot))