    def _load_async_markets(self, reload: bool = False) -> None:
        try:
            if self._api_async:
                asyncio.get_event_loop().run_until_complete(
                    self._api_async.load_markets(reload=reload))

        except ccxt.BaseError as e:
            logger.warning('Could not load async markets. Reason: %s', e)
            return