    async def _do_long_poll(self):
        while True:
            try:
                updates: Dict[str, UpdatedObject] = await self._poll_once()
                self._update(updates)
                logger.debug(f"LongPollerClient received udpates: {updates}")
                for key, updated_object in updates.items():
                    # NOTE(simon):
                    # This blocks the loop from doing another poll. Consider
                    # use loop.create_task here or poll first then call the
                    # callbacks.
                    callback = self.key_listeners[key]
                    await callback(updated_object.object_snapshot)
            except ray.exceptions.RayActorError:
                # This can happen during shutdown where the controller is
                # intentionally killed, the client should just gracefully
                # exit.
                logger.debug("LongPollerClient failed to connect to host. "
                             "Shutting down.")
                break