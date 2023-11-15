    def stop(self):
        """Stop the event loop."""
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
        self.eventloop.stop()