    async def _unsafe_process(self) -> None:
        # If self.pos is None then means we haven't fetched it from DB
        if self.pos is None:
            self.pos = await self.store.get_user_directory_stream_pos()

        # Loop round handling deltas until we're up to date
        while True:
            with Measure(self.clock, "user_dir_delta"):
                room_max_stream_ordering = self.store.get_room_max_stream_ordering()
                if self.pos == room_max_stream_ordering:
                    return

                logger.debug(
                    "Processing user stats %s->%s", self.pos, room_max_stream_ordering
                )
                max_pos, deltas = await self.store.get_current_state_deltas(
                    self.pos, room_max_stream_ordering
                )

                logger.debug("Handling %d state deltas", len(deltas))
                await self._handle_deltas(deltas)

                self.pos = max_pos

                # Expose current event processing position to prometheus
                synapse.metrics.event_processing_positions.labels("user_dir").set(
                    max_pos
                )

                await self.store.update_user_directory_stream_pos(max_pos)