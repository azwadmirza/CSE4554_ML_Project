    def lineReceived(self, line):
        anon_tunnel = self.anon_tunnel

        if line == 'threads':
            for thread in threading.enumerate():
                logger.debug("%s \t %d", thread.name, thread.ident)
        elif line == 'c':
            logger.debug("========\nCircuits\n========\nid\taddress\t\t\t\t\tgoal\thops\tIN (MB)\tOUT (MB)\tinfohash\ttype")
            for circuit_id, circuit in anon_tunnel.community.circuits.items():
                info_hash = circuit.info_hash.encode('hex')[:10] if circuit.info_hash else '?'
                logger.debug("%d\t%s:%d\t%d\t%d\t\t%.2f\t\t%.2f\t\t%s\t%s" % circuit_id,
                                                                       circuit.first_hop[0],
                                                                       circuit.first_hop[1],
                                                                       circuit.goal_hops,
                                                                       len(circuit.hops),
                                                                       circuit.bytes_down / 1024.0 / 1024.0,
                                                                       circuit.bytes_up / 1024.0 / 1024.0,
                                                                       info_hash,
                                                                       circuit.ctype)

        elif line.startswith('s'):
            cur_path = os.getcwd()
            line_split = line.split(' ')
            filename = 'test_file' if len(line_split) == 1 else line_split[1]

            if not os.path.exists(filename):
                logger.info("Creating torrent..")
                with open(filename, 'wb') as fp:
                    fp.write(os.urandom(50 * 1024 * 1024))
                tdef = TorrentDef()
                tdef.add_content(os.path.join(cur_path, filename))
                tdef.set_tracker("udp://localhost/announce")
                tdef.set_private()
                tdef.finalize()
                tdef.save(os.path.join(cur_path, filename + '.torrent'))
            else:
                logger.info("Loading existing torrent..")
                tdef = TorrentDef.load(filename + '.torrent')
            logger.info("loading torrent done, infohash of torrent: %s" % (tdef.get_infohash().encode('hex')[:10]))

            defaultDLConfig = DefaultDownloadStartupConfig.getInstance()
            dscfg = defaultDLConfig.copy()
            dscfg.set_hops(1)
            dscfg.set_dest_dir(cur_path)

            reactor.callFromThread(anon_tunnel.session.start_download_from_tdef, tdef, dscfg)
        elif line.startswith('i'):
            # Introduce dispersy port from other main peer to this peer
            line_split = line.split(' ')
            to_introduce_ip = line_split[1]
            to_introduce_port = int(line_split[2])
            self.anon_tunnel.community.add_discovered_candidate(
                Candidate((to_introduce_ip, to_introduce_port), tunnel=False))
        elif line.startswith('d'):
            line_split = line.split(' ')
            filename = 'test_file' if len(line_split) == 1 else line_split[1]

            logger.info("Loading torrent..")
            tdef = TorrentDef.load(filename + '.torrent')
            logger.info("Loading torrent done")

            defaultDLConfig = DefaultDownloadStartupConfig.getInstance()
            dscfg = defaultDLConfig.copy()
            dscfg.set_hops(1)
            dscfg.set_dest_dir(os.path.join(os.getcwd(), 'downloader%s' % anon_tunnel.session.get_dispersy_port()))

            def start_download():
                def cb(ds):
                    logger.info('Download infohash=%s, down=%s, progress=%s, status=%s, seedpeers=%s, candidates=%d' %
                                (tdef.get_infohash().encode('hex')[:10],
                                 ds.get_current_speed('down'),
                                 ds.get_progress(),
                                 dlstatus_strings[ds.get_status()],
                                 sum(ds.get_num_seeds_peers()),
                                 sum(1 for _ in anon_tunnel.community.dispersy_yield_verified_candidates())))
                    return 1.0, False

                download = anon_tunnel.session.start_download_from_tdef(tdef, dscfg)
                download.set_state_callback(cb)

            reactor.callFromThread(start_download)

        elif line == 'q':
            anon_tunnel.should_run = False

        elif line == 'r':
            logger.debug("circuit\t\t\tdirection\tcircuit\t\t\tTraffic (MB)")
            from_to = anon_tunnel.community.relay_from_to
            for key in from_to.keys():
                relay = from_to[key]
                logger.info("%s-->\t%s\t\t%.2f" % ((key[0], key[1]), (relay.sock_addr, relay.circuit_id),
                                                   relay.bytes[1] / 1024.0 / 1024.0,))