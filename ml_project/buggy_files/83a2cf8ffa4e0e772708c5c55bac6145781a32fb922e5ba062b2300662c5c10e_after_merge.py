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