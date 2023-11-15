    def _maintain_redirects(self):
        # setup the gateway if necessary
        if not self.upnp:
            try:
                self.upnp = yield from_future(UPnP.discover())
                log.info("found upnp gateway: %s", self.upnp.gateway.manufacturer_string)
            except Exception as err:
                log.warning("upnp discovery failed: %s", err)
                return

        # update the external ip
        try:
            external_ip = yield from_future(self.upnp.get_external_ip())
            if external_ip == "0.0.0.0":
                log.warning("upnp doesn't know the external ip address (returned 0.0.0.0), using fallback")
                external_ip = CS.get_external_ip()
            if self.external_ip and self.external_ip != external_ip:
                log.info("external ip changed from %s to %s", self.external_ip, external_ip)
            elif not self.external_ip:
                log.info("got external ip: %s", external_ip)
            self.external_ip = external_ip
        except (asyncio.TimeoutError, UPnPError):
            pass

        if not self.upnp_redirects:  # setup missing redirects
            try:
                upnp_redirects = yield DeferredDict({
                    "UDP": from_future(self.upnp.get_next_mapping(self._int_dht_node_port, "UDP", "LBRY DHT port")),
                    "TCP": from_future(self.upnp.get_next_mapping(self._int_peer_port, "TCP", "LBRY peer port"))
                })
                self.upnp_redirects.update(upnp_redirects)
            except (asyncio.TimeoutError, UPnPError):
                self.upnp = None
                return self._maintain_redirects()
        else:  # check existing redirects are still active
            found = set()
            mappings = yield from_future(self.upnp.get_redirects())
            for mapping in mappings:
                proto = mapping['NewProtocol']
                if proto in self.upnp_redirects and mapping['NewExternalPort'] == self.upnp_redirects[proto]:
                    if mapping['NewInternalClient'] == self.upnp.lan_address:
                        found.add(proto)
            if 'UDP' not in found:
                try:
                    udp_port = yield from_future(
                        self.upnp.get_next_mapping(self._int_dht_node_port, "UDP", "LBRY DHT port")
                    )
                    self.upnp_redirects['UDP'] = udp_port
                    log.info("refreshed upnp redirect for dht port: %i", udp_port)
                except (asyncio.TimeoutError, UPnPError):
                    del self.upnp_redirects['UDP']
            if 'TCP' not in found:
                try:
                    tcp_port = yield from_future(
                        self.upnp.get_next_mapping(self._int_peer_port, "TCP", "LBRY peer port")
                    )
                    self.upnp_redirects['TCP'] = tcp_port
                    log.info("refreshed upnp redirect for peer port: %i", tcp_port)
                except (asyncio.TimeoutError, UPnPError):
                    del self.upnp_redirects['TCP']
            if 'TCP' in self.upnp_redirects and 'UDP' in self.upnp_redirects:
                log.debug("upnp redirects are still active")