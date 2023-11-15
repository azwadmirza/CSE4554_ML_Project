    def create_introduction_point(self, info_hash, amount=1):
        download = self.find_download(info_hash)
        if download:
            download.add_peer(('1.1.1.1', 1024))
        else:
            self.tunnel_logger.error('When creating introduction point: could not find download!')
            return

        # Create a separate key per infohash
        if info_hash not in self.session_keys:
            self.session_keys[info_hash] = self.crypto.generate_key(u"curve25519")

        def callback(circuit):
            # We got a circuit, now let's create an introduction point
            circuit_id = circuit.circuit_id
            self.my_intro_points[circuit_id].append((info_hash))

            cache = self.request_cache.add(IPRequestCache(self, circuit))
            self.send_cell([Candidate(circuit.first_hop, False)],
                           u'establish-intro', (circuit_id, cache.number, info_hash))
            self.tunnel_logger.info("Established introduction tunnel %s", circuit_id)
            if self.notifier:
                self.notifier.notify(NTFY_TUNNEL, NTFY_IP_CREATED, info_hash.encode('hex')[:6], circuit_id)

        for _ in range(amount):
            # Create a circuit to the introduction point + 1 hop, to prevent the introduction
            # point from knowing what the seeder is seeding
            circuit_id = self.create_circuit(self.hops[info_hash] + 1,
                                             CIRCUIT_TYPE_IP,
                                             callback,
                                             info_hash=info_hash)
            self.infohash_ip_circuits[info_hash].append((circuit_id, time.time()))