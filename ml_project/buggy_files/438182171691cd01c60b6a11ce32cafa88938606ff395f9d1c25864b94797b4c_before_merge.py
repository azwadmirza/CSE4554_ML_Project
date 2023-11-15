    async def _do_long_poll(self):
        while True:
            updates: Dict[str, UpdatedObject] = await self._poll_once()
            self._update(updates)
            logger.debug(f"LongPollerClient received updates: {updates}")
            for key, updated_object in updates.items():
                # NOTE(simon): This blocks the loop from doing another poll.
                # Consider use loop.create_task here or poll first then call
                # the callbacks.
                callback = self.key_listeners[key]
                await callback(updated_object.object_snapshot)