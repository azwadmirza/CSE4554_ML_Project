    def _unpack(self, payload, sep=str_to_bytes('\x00\x01')):
        raw_payload = b64decode(ensure_bytes(payload))
        first_sep = raw_payload.find(sep)

        signer = raw_payload[:first_sep]
        signer_cert = self._cert_store[signer]

        # shift 3 bits right to get signature length
        # 2048bit rsa key has a signature length of 256
        # 4096bit rsa key has a signature length of 512
        sig_len = signer_cert.get_pubkey().key_size >> 3
        sep_len = len(sep)
        signature_start_position = first_sep + sep_len
        signature_end_position = signature_start_position + sig_len
        signature = raw_payload[
            signature_start_position:signature_end_position
        ]

        v = raw_payload[signature_end_position + sep_len:].split(sep)

        return {
            'signer': signer,
            'signature': signature,
            'content_type': bytes_to_str(v[0]),
            'content_encoding': bytes_to_str(v[1]),
            'body': bytes_to_str(v[2]),
        }