    def _check_for_async(self):
        if self.config.check_for_async:
            in_async = False
            if sys.version_info >= (3, 7, 0):
                try:
                    asyncio.get_running_loop()
                    in_async = True
                except RuntimeError:
                    pass
            else:  # pragma: no cover # not able to be covered in > Python 3.6.12
                in_async = asyncio.get_event_loop().is_running()
            if in_async:
                logger.warning(
                    "It appears that you are using PRAW in an asynchronous"
                    " environment.\nIt is strongly recommended to use Async PRAW:"
                    " https://asyncpraw.readthedocs.io.\nSee"
                    " https://praw.readthedocs.io/en/latest/getting_started/multiple_instances.html#discord-bots-and-asynchronous-environments"
                    " for more info.\n",
                )