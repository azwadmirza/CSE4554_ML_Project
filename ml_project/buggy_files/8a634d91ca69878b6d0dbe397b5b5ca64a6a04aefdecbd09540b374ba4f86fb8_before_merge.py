    def load_ipv8_overlays(self):
        # Discovery Community
        with open(self.session.config.get_permid_keypair_filename(), 'r') as key_file:
            content = key_file.read()
        content = content[31:-30].replace('\n', '').decode("BASE64")
        peer = Peer(M2CryptoSK(keystring=content))
        discovery_community = DiscoveryCommunity(peer, self.ipv8.endpoint, self.ipv8.network)
        discovery_community.resolve_dns_bootstrap_addresses()
        self.ipv8.overlays.append(discovery_community)
        self.ipv8.strategies.append((RandomChurn(discovery_community), -1))

        if not self.session.config.get_dispersy_enabled():
            self.ipv8.strategies.append((RandomWalk(discovery_community), 20))

        if self.session.config.get_testnet():
            peer = Peer(self.session.trustchain_keypair)
        else:
            peer = Peer(self.session.trustchain_testnet_keypair)

        # TrustChain Community
        if self.session.config.get_trustchain_enabled():
            from Tribler.pyipv8.ipv8.attestation.trustchain.community import TrustChainCommunity, \
                TrustChainTestnetCommunity

            community_cls = TrustChainTestnetCommunity if self.session.config.get_testnet() else TrustChainCommunity
            self.trustchain_community = community_cls(peer, self.ipv8.endpoint,
                                                      self.ipv8.network,
                                                      working_directory=self.session.config.get_state_dir())
            self.ipv8.overlays.append(self.trustchain_community)
            self.ipv8.strategies.append((EdgeWalk(self.trustchain_community), 20))

            tc_wallet = TrustchainWallet(self.trustchain_community)
            self.wallets[tc_wallet.get_identifier()] = tc_wallet

        # DHT Community
        if self.session.config.get_dht_enabled():
            from Tribler.pyipv8.ipv8.dht.discovery import DHTDiscoveryCommunity

            dht_peer = Peer(self.session.trustchain_keypair)
            self.dht_community = DHTDiscoveryCommunity(dht_peer, self.ipv8.endpoint, self.ipv8.network)
            self.ipv8.overlays.append(self.dht_community)
            self.ipv8.strategies.append((RandomWalk(self.dht_community), 20))

        # Tunnel Community
        if self.session.config.get_tunnel_community_enabled():

            from Tribler.community.triblertunnel.community import TriblerTunnelCommunity, TriblerTunnelTestnetCommunity
            community_cls = TriblerTunnelTestnetCommunity if self.session.config.get_testnet() else \
                TriblerTunnelCommunity
            self.tunnel_community = community_cls(peer, self.ipv8.endpoint, self.ipv8.network,
                                                  tribler_session=self.session,
                                                  dht_provider=MainlineDHTProvider(
                                                      self.mainline_dht,
                                                      self.session.config.get_dispersy_port()),
                                                  bandwidth_wallet=self.wallets["MB"])
            self.ipv8.overlays.append(self.tunnel_community)
            self.ipv8.strategies.append((RandomWalk(self.tunnel_community), 20))

        # Market Community
        if self.session.config.get_market_community_enabled():
            from Tribler.community.market.community import MarketCommunity, MarketTestnetCommunity

            community_cls = MarketTestnetCommunity if self.session.config.get_testnet() else MarketCommunity
            self.market_community = community_cls(peer, self.ipv8.endpoint, self.ipv8.network,
                                                  tribler_session=self.session,
                                                  trustchain=self.trustchain_community,
                                                  wallets=self.wallets,
                                                  working_directory=self.session.config.get_state_dir())

            self.ipv8.overlays.append(self.market_community)

            self.ipv8.strategies.append((RandomWalk(self.market_community), 20))

        # Popular Community
        if self.session.config.get_popularity_community_enabled():
            from Tribler.community.popularity.community import PopularityCommunity

            self.popularity_community = PopularityCommunity(peer, self.ipv8.endpoint, self.ipv8.network,
                                                            torrent_db=self.session.lm.torrent_db, session=self.session)

            self.ipv8.overlays.append(self.popularity_community)

            self.ipv8.strategies.append((RandomWalk(self.popularity_community), 20))

            self.popularity_community.start()