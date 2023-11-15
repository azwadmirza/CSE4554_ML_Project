    async def update_token(self, token):
        """Update the record of where we have processed to in the federation stream.

        Called after we have processed a an update received over replication. Sends
        a FEDERATION_ACK back to the master, and stores the token that we have processed
         in `federation_stream_position` so that we can restart where we left off.
        """
        try:
            self.federation_position = token

            # We linearize here to ensure we don't have races updating the token
            #
            # XXX this appears to be redundant, since the ReplicationCommandHandler
            # has a linearizer which ensures that we only process one line of
            # replication data at a time. Should we remove it, or is it doing useful
            # service for robustness? Or could we replace it with an assertion that
            # we're not being re-entered?

            with (await self._fed_position_linearizer.queue(None)):
                await self.store.update_federation_out_pos(
                    "federation", self.federation_position
                )

                # We ACK this token over replication so that the master can drop
                # its in memory queues
                self._hs.get_tcp_replication().send_federation_ack(
                    self.federation_position
                )
                self._last_ack = self.federation_position
        except Exception:
            logger.exception("Error updating federation stream position")