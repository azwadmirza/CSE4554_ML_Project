    def send_request(self, request):
        data = (request.format(),)
        payload = zlib.compress(rencode.dumps(data))
        self.conn.sendall(payload)

        buf = b""

        while True:
            data = self.conn.recv(1024)

            if not data:
                self.connected = False
                break

            buf += data
            dobj = zlib.decompressobj()

            try:
                message = rencode.loads(dobj.decompress(buf), decode_utf8=True)
            except (ValueError, zlib.error, struct.error):
                # Probably incomplete data, read more
                continue
            else:
                buf = dobj.unused_data

            yield message