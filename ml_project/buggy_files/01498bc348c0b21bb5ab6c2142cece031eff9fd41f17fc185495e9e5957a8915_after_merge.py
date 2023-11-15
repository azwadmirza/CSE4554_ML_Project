    def subscribe_to_stream(self, stream_name, token):
        """Subscribe the remote to a stream.

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
            updates = []
            for token, update in pending_rdata:
                # If the token is null, it is part of a batch update. Batches
                # are multiple updates that share a single token. To denote
                # this, the token is set to None for all tokens in the batch
                # except for the last. If we find a None token, we keep looking
                # through tokens until we find one that is not None and then
                # process all previous updates in the batch as if they had the
                # final token.
                if token is None:
                    # Store this update as part of a batch
                    updates.append(update)
                    continue

                if token <= current_token:
                    # This update or batch of updates is older than
                    # current_token, dismiss it
                    updates = []
                    continue

                updates.append(update)

                # Send all updates that are part of this batch with the
                # found token
                for update in updates:
                    self.send_command(RdataCommand(stream_name, token, update))

                # Clear stored updates
                updates = []

            # They're now fully subscribed
            self.replication_streams.add(stream_name)
        except Exception as e:
            logger.exception("[%s] Failed to handle REPLICATE command", self.id())
            self.send_error("failed to handle replicate: %r", e)
        finally:
            self.connecting_streams.discard(stream_name)