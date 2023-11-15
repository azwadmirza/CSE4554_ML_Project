    def subscribe_to_stream(self, stream_name, token):
        """Subscribe the remote to a streams.

        This invloves checking if they've missed anything and sending those
        updates down if they have. During that time new updates for the stream
        are queued and sent once we've sent down any missed updates.
        """
        self.replication_streams.discard(stream_name)
        self.connecting_streams.add(stream_name)

        try:
            # Get missing updates
            updates, current_token = yield self.streamer.get_stream_updates(
                stream_name, token,
            )

            # Send all the missing updates
            for update in updates:
                token, row = update[0], update[1]
                self.send_command(RdataCommand(stream_name, token, row))

            # We send a POSITION command to ensure that they have an up to
            # date token (especially useful if we didn't send any updates
            # above)
            self.send_command(PositionCommand(stream_name, current_token))

            # Now we can send any updates that came in while we were subscribing
            pending_rdata = self.pending_rdata.pop(stream_name, [])
            for token, update in pending_rdata:
                # Only send updates newer than the current token
                if token > current_token:
                    self.send_command(RdataCommand(stream_name, token, update))

            # They're now fully subscribed
            self.replication_streams.add(stream_name)
        except Exception as e:
            logger.exception("[%s] Failed to handle REPLICATE command", self.id())
            self.send_error("failed to handle replicate: %r", e)
        finally:
            self.connecting_streams.discard(stream_name)