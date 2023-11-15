    def stream_protocol_messages(self,
                                 protocol_identifier: Union[ProtocolAPI, Type[ProtocolAPI]],
                                 ) -> AsyncIterator[CommandAPI[Any]]:
        """
        Stream the messages for the specified protocol.
        """
        if isinstance(protocol_identifier, ProtocolAPI):
            protocol_class = type(protocol_identifier)
        elif isinstance(protocol_identifier, type) and issubclass(protocol_identifier, ProtocolAPI):
            protocol_class = protocol_identifier
        else:
            raise TypeError("Unknown protocol identifier: {protocol}")

        if not self.has_protocol(protocol_class):
            raise UnknownProtocol(f"Unknown protocol '{protocol_class}'")

        if self._protocol_locks[protocol_class].locked():
            raise Exception(f"Streaming lock for {protocol_class} is not free.")
        elif not self._multiplex_lock.locked():
            raise Exception("Not multiplexed.")

        # Mostly a sanity check but this ensures we do better than accidentally
        # raising an attribute error in whatever race conditions or edge cases
        # potentially make the `_multiplex_token` unavailable.
        if not hasattr(self, '_multiplex_token'):
            raise Exception("No cancel token found for multiplexing.")

        # We do the wait_iter here so that the call sites in the handshakers
        # that use this don't need to be aware of cancellation tokens.
        return self.wait_iter(
            self._stream_protocol_messages(protocol_class),
            token=self._multiplex_token,
        )