    def take_step(self):
        """
        We are asked to update, see if we have enough peers to start culling them.
        If we do have enough peers, select a suitable peer to remove.

        :returns: None
        """
        with self.walk_lock:
            peers = self.overlay.get_peers()
            for peer in list(self.intro_sent.keys()):
                if peer not in peers:
                    self.intro_sent.pop(peer, None)

            # Some of the peers in the community could have been discovered using the DiscoveryCommunity. If this
            # happens we have no knowledge of their peer_flags. In order to still get the flags we send them an
            # introduction request manually.
            now = time.time()
            for peer in peers:
                if peer not in self.overlay.candidates and now > self.intro_sent.get(peer, 0) + 300:
                    self.overlay.send_introduction_request(peer)
                    self.intro_sent[peer] = now

            peer_count = len(peers)
            if peer_count > self.target_peers:
                exit_peers = set(self.overlay.get_candidates(PEER_FLAG_EXIT_BT))
                exit_count = len(exit_peers)
                ratio = 1.0 - exit_count / peer_count  # Peer count is > 0 per definition
                if ratio < self.golden_ratio:
                    self.overlay.network.remove_peer(sample(exit_peers, 1)[0])
                elif ratio > self.golden_ratio:
                    self.overlay.network.remove_peer(sample(set(self.overlay.get_peers()) - exit_peers, 1)[0])