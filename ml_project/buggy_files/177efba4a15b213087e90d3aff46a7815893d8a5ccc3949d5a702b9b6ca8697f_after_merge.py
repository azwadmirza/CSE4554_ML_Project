    async def lock(
        self,
        conversation_id: Text,
        lock_lifetime: float = LOCK_LIFETIME,
        wait_time_in_seconds: float = 1,
    ) -> AsyncGenerator[TicketLock, None]:
        """Acquire lock with lifetime `lock_lifetime`for `conversation_id`.

        Try acquiring lock with a wait time of `wait_time_in_seconds` seconds
        between attempts. Raise a `LockError` if lock has expired.
        """

        ticket = self.issue_ticket(conversation_id, lock_lifetime)

        try:
            yield await self._acquire_lock(
                conversation_id, ticket, wait_time_in_seconds
            )

        finally:
            self.cleanup(conversation_id, ticket)