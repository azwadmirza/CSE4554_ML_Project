        def do_check():
            with self.dllock:
                if not self.cew_scheduled:
                    self.ltmgr = self.session.lm.ltmgr
                    dht_ok = not isinstance(self.tdef, TorrentDefNoMetainfo) or self.ltmgr.is_dht_ready()
                    tunnel_community = self.ltmgr.tribler_session.lm.tunnel_community
                    tunnels_ready = tunnel_community.tunnels_ready(self.get_hops()) if tunnel_community else 1

                    if not self.ltmgr or not dht_ok or tunnels_ready < 1:
                        self._logger.info(u"LTMGR/DHT/session not ready, rescheduling create_engine_wrapper")

                        if tunnel_community and tunnels_ready < 1:
                            tunnel_community.build_tunnels(self.get_hops())

                        # Schedule this function call to be called again in 5 seconds
                        self.register_task("check_create_wrapper", reactor.callLater(5, do_check))
                    else:
                        can_create_deferred.callback(True)
                else:
                    # Schedule this function call to be called again in 5 seconds
                    self.register_task("check_create_wrapper", reactor.callLater(5, do_check))