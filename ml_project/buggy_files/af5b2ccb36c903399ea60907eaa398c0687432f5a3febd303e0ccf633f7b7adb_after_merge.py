    def __await__(self):
        # Register AsyncOperationCompletedHandler callback that triggers the above asyncio.Event.
        self.operation.Completed = AsyncOperationCompletedHandler[self.return_type](
            lambda x, y: self._loop.call_soon_threadsafe(self.done.set)
        )
        yield from self.done.wait()
        return self