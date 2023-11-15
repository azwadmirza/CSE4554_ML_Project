    async def _refresh_time_frame_data(self, time_frame, symbol, notify=True):
        try:
            await self._refresh_data(time_frame, symbol, notify=notify)
            self.time_frame_last_update[time_frame][symbol] = time.time()
        except CancelledError as e:
            raise e
        except Exception as e:
            self.logger.error(f" when refreshing data for time frame {time_frame}: {e}")
            self.logger.exception(e)