    async def _cleanup(self) -> None:
        for rule_name, rule_id in self._rules.items():
            logger.debug("Removing rule {0}, ID: {1}".format(rule_name, rule_id))
            await self._bus.delMatch(rule_id).asFuture(self.loop)

        await asyncio.gather(
            *(self.stop_notify(_uuid) for _uuid in self._subscriptions)
        )