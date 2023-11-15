    async def _acquire_lock(
        self, conversation_id: Text, ticket: int, wait_time_in_seconds: float,
    ) -> TicketLock:

        while True:
            # fetch lock in every iteration because lock might no longer exist
            lock = self.get_lock(conversation_id)

            # exit loop if lock does not exist anymore (expired)
            if not lock:
                break

            # acquire lock if it isn't locked
            if not lock.is_locked(ticket):
                return lock

            logger.debug(
                f"Failed to acquire lock for conversation ID '{conversation_id}'. "
                f"Retrying..."
            )

            # sleep and update lock
            await asyncio.sleep(wait_time_in_seconds)
            self.update_lock(conversation_id)

        raise LockError(
            f"Could not acquire lock for conversation_id '{conversation_id}'."
        )