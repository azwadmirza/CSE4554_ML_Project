        async def wrapper(*args, **kwargs):
            task = self._loop_create_task(func(*args, **kwargs))
            task.add_done_callback(process_response)