    def _unpack(self, payload, sep=str_to_bytes('\x00\x01')):
        raw_payload = b64decode(ensure_bytes(payload))
        first_sep = raw_payload.find(sep)

        signer = raw_payload[:first_sep]
        signer_cert = self._cert_store[signer]

        sig_len = signer_cert._cert.get_pubkey().bits() >> 3
        signature = raw_payload[
            first_sep + len(sep):first_sep + len(sep) + sig_len
        ]
        end_of_sig = first_sep + len(sep) + sig_len + len(sep)

        v = raw_payload[end_of_sig:].split(sep)

        return {
            'signer': signer,
            'signature': signature,
            'content_type': bytes_to_str(v[0]),
            'content_encoding': bytes_to_str(v[1]),
            'body': bytes_to_str(v[2]),
        }