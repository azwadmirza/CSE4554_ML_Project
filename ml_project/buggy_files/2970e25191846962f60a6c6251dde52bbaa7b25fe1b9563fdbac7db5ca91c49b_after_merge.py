    def lock_node_for_handshake(self, node: NodeAPI) -> AsyncContextManager[None]:
        return self._handshake_locks.lock(node)