    def __init__(self, controller_handle, sync: bool):
        self.router = Router(controller_handle)

        if sync:
            self.async_loop = create_or_get_async_loop_in_thread()
            asyncio.run_coroutine_threadsafe(
                self.router.setup_in_async_loop(),
                self.async_loop,
            )
        else:
            self.async_loop = asyncio.get_event_loop()
            self.async_loop.create_task(self.router.setup_in_async_loop())