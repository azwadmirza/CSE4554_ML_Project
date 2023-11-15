    def on_created_e2e(self, messages):
        for message in messages:
            cache = self.request_cache.pop(u"e2e-request", message.payload.identifier)
            shared_secret = self.crypto.verify_and_generate_shared_secret(cache.hop.dh_secret,
                                                                          message.payload.key,
                                                                          message.payload.auth,
                                                                          cache.hop.public_key.key.pk)
            session_keys = self.crypto.generate_session_keys(shared_secret)

            _, decoded = decode(self.crypto.decrypt_str(message.payload.rp_sock_addr,
                                                        session_keys[EXIT_NODE],
                                                        session_keys[EXIT_NODE_SALT]))
            rp_info, cookie = decoded

            if self.notifier:
                self.notifier.notify(NTFY_TUNNEL, NTFY_ONCREATED_E2E, cache.info_hash.encode('hex')[:6], rp_info)

            # Since it is the seeder that chose the rendezvous_point, we're essentially losing 1 hop of anonymity
            # at the downloader end. To compensate we add an extra hop.
            required_exit = Candidate(rp_info[:2], False)
            required_exit.associate(self.get_member(public_key=rp_info[2]))
            self.create_circuit(self.hops[cache.info_hash] + 1,
                                CIRCUIT_TYPE_RENDEZVOUS,
                                callback=lambda circuit, cookie=cookie, session_keys=session_keys,
                                info_hash=cache.info_hash, sock_addr=cache.sock_addr: self.create_link_e2e(circuit,
                                                                                                           cookie,
                                                                                                           session_keys,
                                                                                                           info_hash,
                                                                                                           sock_addr),
                                required_exit=required_exit,
                                info_hash=cache.info_hash)