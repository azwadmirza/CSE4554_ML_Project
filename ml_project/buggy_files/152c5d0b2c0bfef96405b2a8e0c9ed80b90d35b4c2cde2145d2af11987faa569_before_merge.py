    def query_random_peer(self) -> None:
        """
        Query a random peer neighbouring peer and ask their bandwidth transactions.
        """
        peers = list(self.network.verified_peers)
        random_peer = self.random.choice(peers)
        if random_peer:
            self.query_transactions(random_peer)