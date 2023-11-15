    def stop(self):
        """Stop the event loop."""
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
        self.eventloop.stop()
        print('')  # Prints a character return for return to shell
        _LOGGER.info("Keyboard interrupt, exiting.")