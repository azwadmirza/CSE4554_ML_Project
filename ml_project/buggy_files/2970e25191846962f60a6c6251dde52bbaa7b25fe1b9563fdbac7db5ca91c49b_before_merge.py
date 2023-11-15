    def lock_node_for_handshake(self, node: NodeAPI) -> asyncio.Lock:
        return self._handshake_locks.lock(node)