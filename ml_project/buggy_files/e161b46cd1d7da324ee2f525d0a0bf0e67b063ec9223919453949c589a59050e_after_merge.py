    def on_torrent_health_check_completed(self, infohash, result):
        final_response = {}
        if not result or not isinstance(result, list):
            self._logger.info("Received invalid torrent checker result")
            self.tribler_session.notifier.notify(NTFY_TORRENT, NTFY_UPDATE, infohash,
                                                 {"num_seeders": 0,
                                                  "num_leechers": 0,
                                                  "last_tracker_check": int(time.time()),
                                                  "health": "updated"})
            return final_response

        torrent_update_dict = {'infohash': infohash, 'seeders': 0, 'leechers': 0, 'last_check': int(time.time())}
        for success, response in reversed(result):
            if not success and isinstance(response, Failure):
                final_response[response.tracker_url] = {'error': response.getErrorMessage()}
                continue
            elif response is None:
                self._logger.warning("Torrent health response is none!")
                continue
            final_response[response.keys()[0]] = response[response.keys()[0]][0]

            s = response[response.keys()[0]][0]['seeders']
            l = response[response.keys()[0]][0]['leechers']

            # More leeches is better, because undefined peers are marked as leeches in DHT
            if s > torrent_update_dict['seeders'] or \
                    (s == torrent_update_dict['seeders'] and l > torrent_update_dict['leechers']):
                torrent_update_dict['seeders'] = s
                torrent_update_dict['leechers'] = l

        self._update_torrent_result(torrent_update_dict)
        self.update_torrents_checked(torrent_update_dict)

        # TODO: DRY! Stop doing lots of formats, just make REST endpoint automatically encode binary data to hex!
        self.tribler_session.notifier.notify(NTFY_TORRENT, NTFY_UPDATE, infohash,
                                             {"num_seeders": torrent_update_dict["seeders"],
                                              "num_leechers": torrent_update_dict["leechers"],
                                              "last_tracker_check": torrent_update_dict["last_check"],
                                              "health": "updated"})
        return final_response