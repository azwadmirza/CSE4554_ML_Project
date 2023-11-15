    def async_task(self, func):
        """
        Execute handler as task and return None.
        Use this decorator for slow handlers (with timeouts)

        .. code-block:: python3

            @dp.message_handler(commands=['command'])
            @dp.async_task
            async def cmd_with_timeout(message: types.Message):
                await asyncio.sleep(120)
                return SendMessage(message.chat.id, 'KABOOM').reply(message)

        :param func:
        :return:
        """

        def process_response(task):
            try:
                response = task.result()
            except Exception as e:
                self._loop_create_task(
                    self.errors_handlers.notify(types.Update.get_current(), e))
            else:
                if isinstance(response, BaseResponse):
                    self._loop_create_task(response.execute_response(self.bot))

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            task = self._loop_create_task(func(*args, **kwargs))
            task.add_done_callback(process_response)

        return wrapper