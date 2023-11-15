    async def update_token(self, token):
        try:
            self.federation_position = token

            # We linearize here to ensure we don't have races updating the token
            with (await self._fed_position_linearizer.queue(None)):
                if self._last_ack < self.federation_position:
                    await self.store.update_federation_out_pos(
                        "federation", self.federation_position
                    )

                    # We ACK this token over replication so that the master can drop
                    # its in memory queues
                    self.replication_client.send_federation_ack(
                        self.federation_position
                    )
                    self._last_ack = self.federation_position
        except Exception:
            logger.exception("Error updating federation stream position")