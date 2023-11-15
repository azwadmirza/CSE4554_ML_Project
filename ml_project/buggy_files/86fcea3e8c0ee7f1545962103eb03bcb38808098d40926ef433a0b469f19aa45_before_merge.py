    def connect_to_tracker(self):
        """
        Fakely connects to a tracker.
        :return: A deferred that fires with the health information.
        """
        def on_metainfo(metainfo):
            if not metainfo:
                self.result_deferred.errback(Failure(RuntimeError("Metainfo lookup error")))
                return

            self.result_deferred.callback({
                "DHT": [{
                    "infohash": hexlify(self.infohash),
                    "seeders": metainfo["seeders"],
                    "leechers": metainfo["leechers"]
                }]
            })

        self._session.lm.ltmgr.get_metainfo(self.infohash, timeout=self.timeout).addCallback(on_metainfo)
        return self.result_deferred