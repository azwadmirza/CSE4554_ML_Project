    async def listen(self):
        """Listen method of the connector.

        Every connector has to implement the listen method. When an
        infinite loop is running, it becomes hard to cancel this task.
        So we are creating a task and set it on a variable so we can
        cancel the task.

        """
        message_getter = self.loop.create_task(self.get_messages_loop())
        await self._closing.wait()
        message_getter.cancel()