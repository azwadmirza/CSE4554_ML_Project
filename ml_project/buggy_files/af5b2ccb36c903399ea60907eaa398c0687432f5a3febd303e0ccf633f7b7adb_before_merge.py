    def __await__(self):
        def callback(task):
            self._loop.call_soon_threadsafe(self.done.set)

        self.task.ContinueWith(Action[Task](callback))
        yield from self.done.wait()
        return self