    async def _stream_protocol_messages(self,
                                        protocol_class: Type[ProtocolAPI],
                                        ) -> AsyncIterator[CommandAPI[Any]]:
        """
        Stream the messages for the specified protocol.
        """
        async with self._protocol_locks[protocol_class]:
            msg_queue = self._protocol_queues[protocol_class]
            if not hasattr(self, '_multiplex_token'):
                raise Exception("Multiplexer is not multiplexed")
            token = self._multiplex_token

            while not self.is_closing and not token.triggered:
                try:
                    # We use an optimistic strategy here of using
                    # `get_nowait()` to reduce the number of times we yield to
                    # the event loop.  Since this is an async generator it will
                    # yield to the loop each time it returns a value so we
                    # don't have to worry about this blocking other processes.
                    yield msg_queue.get_nowait()
                except asyncio.QueueEmpty:
                    yield await msg_queue.get()