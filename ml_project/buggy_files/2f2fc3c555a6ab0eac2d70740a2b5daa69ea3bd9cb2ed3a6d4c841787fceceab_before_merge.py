    def cache_exitnodes_to_disk(self):
        """
        Wite a copy of the exit_candidates to the file self.exitnode_cache.

        :returns: None
        """
        exit_nodes = Network()
        for peer in self.get_candidates(PEER_FLAG_EXIT_ANY):
            exit_nodes.add_verified_peer(peer)
        self.logger.debug('Writing exit nodes to cache: %s', self.exitnode_cache)
        with open(self.exitnode_cache, 'wb') as cache:
            cache.write(exit_nodes.snapshot())