    def take_step(self):
        """
        We are asked to update, see if we have enough peers to start culling them.
        If we do have enough peers, select a suitable peer to remove.

        :returns: None
        """
        with self.walk_lock:
            peer_count = len(self.overlay.get_peers())
            if peer_count > self.target_peers:
                exit_peers = set(self.overlay.get_candidates(PEER_FLAG_EXIT_ANY))
                exit_count = len(exit_peers)
                ratio = 1.0 - exit_count / peer_count  # Peer count is > 0 per definition
                if ratio < self.golden_ratio:
                    self.overlay.network.remove_peer(sample(exit_peers, 1)[0])
                elif ratio > self.golden_ratio:
                    self.overlay.network.remove_peer(sample(set(self.overlay.get_peers()) - exit_peers, 1)[0])