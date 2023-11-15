    def start(self):
        self.upnp_component = self.component_manager.get_component(UPNP_COMPONENT)
        self.external_peer_port = self.upnp_component.upnp_redirects.get("TCP", GCS("peer_port"))
        self.external_udp_port = self.upnp_component.upnp_redirects.get("UDP", GCS("dht_node_port"))
        node_id = CS.get_node_id()
        if node_id is None:
            node_id = generate_id()
        external_ip = self.upnp_component.external_ip
        if not external_ip:
            log.warning("UPnP component failed to get external ip")
            external_ip = CS.get_external_ip()
            if not external_ip:
                log.warning("failed to get external ip")

        self.dht_node = node.Node(
            node_id=node_id,
            udpPort=GCS('dht_node_port'),
            externalUDPPort=self.external_udp_port,
            externalIP=external_ip,
            peerPort=self.external_peer_port
        )

        self.dht_node.start_listening()
        yield self.dht_node._protocol._listening
        d = self.dht_node.joinNetwork(GCS('known_dht_nodes'))
        d.addCallback(lambda _: self.dht_node.start_looping_calls())
        d.addCallback(lambda _: log.info("Joined the dht"))
        log.info("Started the dht")