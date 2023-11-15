    async def do_payout(self, mid):
        """
        Perform a payout to a given mid. First, determine the outstanding balance. Then resolve the node in the DHT.
        """
        if mid not in self.tribler_peers:
            return None

        total_bytes = sum(self.tribler_peers[mid].values())

        self.logger.info("Doing direct payout to %s (%d bytes)", hexlify(mid), total_bytes)
        try:
            nodes = await self.dht.connect_peer(mid)
        except Exception as e:
            self.logger.warning("Error while doing DHT lookup for payouts, error %s", e)
            return None

        self.logger.debug("Received %d nodes for DHT lookup", len(nodes))
        if nodes:
            try:
                await self.bandwidth_community.do_payout(nodes[0], total_bytes)
            except Exception as e:
                self.logger.error("Error while doing bandwidth payout, error %s", e)
                return None

        # Remove the outstanding bytes; otherwise we will payout again
        self.tribler_peers.pop(mid, None)
        return nodes[0]