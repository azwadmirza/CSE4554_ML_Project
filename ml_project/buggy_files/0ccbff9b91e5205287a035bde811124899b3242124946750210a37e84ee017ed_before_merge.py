    async def start_update_loop(self):

        error = None
        try:
            time_frames = self.evaluator_task_manager_by_time_frame_by_symbol.keys()

            # sort time frames to update them in order of accuracy
            time_frames = TimeFrameManager.sort_time_frames(time_frames)

            if time_frames and self.symbols:

                self.in_backtesting = self._init_backtesting_if_necessary(time_frames)

                # init refreshed_times at 0 for each time frame
                self.refreshed_times = {key: {symbol: 0 for symbol in self.symbols} for key in time_frames}

                # init last refresh times at 0 for each time frame
                self.time_frame_last_update = {key: {symbol: 0 for symbol in self.symbols} for key in time_frames}

                while self.keep_running:
                    try:
                        await self._trigger_update(time_frames)
                    except Exception as e:
                        self.logger.error(f"exception when triggering update: {e}")
                        self.logger.exception(e)
            else:
                self.logger.warning("no time frames to monitor, going to sleep.")

        except Exception as e:
            self.logger.exception(e)
            if self.watcher is not None:
                error = e

        finally:
            if self.in_backtesting \
                    and self.symbols is not None \
                    and not self.exchange.get_exchange().get_backtesting().get_is_finished(self.symbols):
                if error is None:
                    error = "backtesting did not finish properly."
                if self.watcher is not None:
                    self.watcher.set_error(error)
                self.logger.error(error)