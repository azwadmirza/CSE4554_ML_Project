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