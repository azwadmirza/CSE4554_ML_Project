    async def purge_history(
        self, room_id: str, token: str, delete_local_events: bool
    ) -> Set[int]:
        """Deletes room history before a certain point.

        Note that only a single purge can occur at once, this is guaranteed via
        a higher level (in the PaginationHandler).

        Args:
            room_id:
            token: A topological token to delete events before
            delete_local_events:
                if True, we will delete local events as well as remote ones
                (instead of just marking them as outliers and deleting their
                state groups).

        Returns:
            The set of state groups that are referenced by deleted events.
        """

        parsed_token = await RoomStreamToken.parse(self, token)

        return await self.db_pool.runInteraction(
            "purge_history",
            self._purge_history_txn,
            room_id,
            parsed_token,
            delete_local_events,
        )