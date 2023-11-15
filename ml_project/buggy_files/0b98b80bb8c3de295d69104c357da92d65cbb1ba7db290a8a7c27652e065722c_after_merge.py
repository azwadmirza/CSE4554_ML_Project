    async def start_polling(self,
                            timeout=20,
                            relax=0.1,
                            limit=None,
                            reset_webhook=None,
                            fast: typing.Optional[bool] = True,
                            error_sleep: int = 5):
        """
        Start long-polling

        :param timeout:
        :param relax:
        :param limit:
        :param reset_webhook:
        :param fast:
        :return:
        """
        if self._polling:
            raise RuntimeError('Polling already started')

        log.info('Start polling.')

        # context.set_value(MODE, LONG_POLLING)
        Dispatcher.set_current(self)
        Bot.set_current(self.bot)

        if reset_webhook is None:
            await self.reset_webhook(check=False)
        if reset_webhook:
            await self.reset_webhook(check=True)

        self._polling = True
        offset = None
        try:
            current_request_timeout = self.bot.timeout
            if current_request_timeout is not sentinel and timeout is not None:
                request_timeout = aiohttp.ClientTimeout(total=current_request_timeout.total + timeout or 1)
            else:
                request_timeout = None

            while self._polling:
                try:
                    with self.bot.request_timeout(request_timeout):
                        updates = await self.bot.get_updates(limit=limit, offset=offset, timeout=timeout)
                except asyncio.CancelledError:
                    break
                except:
                    log.exception('Cause exception while getting updates.')
                    await asyncio.sleep(error_sleep)
                    continue

                if updates:
                    log.debug(f"Received {len(updates)} updates.")
                    offset = updates[-1].update_id + 1

                    self._loop_create_task(self._process_polling_updates(updates, fast))

                if relax:
                    await asyncio.sleep(relax)

        finally:
            self._close_waiter.set_result(None)
            log.warning('Polling is stopped.')