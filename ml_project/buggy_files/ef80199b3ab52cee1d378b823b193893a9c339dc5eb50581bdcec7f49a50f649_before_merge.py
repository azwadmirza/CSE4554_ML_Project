    def _check_for_async(self):
        if self.config.check_for_async:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                pass
            else:
                logger.warning(
                    "It appears that you are using PRAW in an asynchronous"
                    " environment.\nIt is strongly recommended to use Async PRAW:"
                    " https://asyncpraw.readthedocs.io.\nSee"
                    " https://praw.readthedocs.io/en/latest/getting_started/multiple_instances.html#discord-bots-and-asynchronous-environments"
                    " for more info.\n",
                )