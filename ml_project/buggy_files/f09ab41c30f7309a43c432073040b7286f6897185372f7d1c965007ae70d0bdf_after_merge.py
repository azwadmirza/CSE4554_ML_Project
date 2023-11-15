    def encode_callback(self, key, conn):
        encoding_map = {
            "z": "gzip",
            "d": "deflate",
            "b": "br",
        }
        conn.encode(encoding_map[key])
        signals.flow_change.send(self, flow = self.flow)