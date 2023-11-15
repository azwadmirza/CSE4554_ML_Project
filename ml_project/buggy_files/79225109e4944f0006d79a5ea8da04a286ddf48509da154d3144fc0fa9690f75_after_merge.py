    async def connect_to_node(self, node: NodeAPI) -> None:
        """
        Connect to a single node quietly aborting if the peer pool is full or
        shutting down, or one of the expected peer level exceptions is raised
        while connecting.
        """
        if self.is_full or not self.manager.is_running:
            self.logger.warning("Asked to connect to node when either full or not operational")
            return

        if self._handshake_locks.is_locked(node):
            self.logger.info(
                "Asked to connect to node when handshake lock is already locked, will wait")

        async with self.lock_node_for_handshake(node):
            if self.is_connected_to_node(node):
                self.logger.debug(
                    "Aborting outbound connection attempt to %s. Already connected!",
                    node,
                )
                return

            try:
                async with self._connection_attempt_lock:
                    peer = await self.connect(node)
            except ALLOWED_PEER_CONNECTION_EXCEPTIONS:
                return

            await self.add_outbound_peer(peer)