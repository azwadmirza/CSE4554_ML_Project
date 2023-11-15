    async def _cleanup(self) -> None:
        for rule_name, rule_id in self._rules.items():
            logger.debug("Removing rule {0}, ID: {1}".format(rule_name, rule_id))
            try:
                await self._bus.delMatch(rule_id).asFuture(self.loop)
            except Exception as e:
                logger.error("Could not remove rule {0} ({1}): {2}".format(rule_id, rule_name, e))
        self._rules = {}

        for _uuid in list(self._subscriptions):
            try:
                await self.stop_notify(_uuid)
            except Exception as e:
                logger.error("Could not remove notifications on characteristic {0}: {1}".format(_uuid, e))
        self._subscriptions = []