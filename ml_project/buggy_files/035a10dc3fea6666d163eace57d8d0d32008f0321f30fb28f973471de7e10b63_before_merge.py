    def m2i(self, pkt, m):
        s = pkt.tls_session
        tmp_len = self.length_from(pkt)
        if s.prcs:
            cls = s.prcs.key_exchange.server_kx_msg_cls(m)
            if cls is None:
                return None, Raw(m[:tmp_len]) / Padding(m[tmp_len:])
            return cls(m, tls_session=s)
        else:
            try:
                p = ServerDHParams(m, tls_session=s)
                if pkcs_os2ip(p.load[:2]) not in _tls_hash_sig:
                    raise Exception
                return p
            except Exception:
                cls = _tls_server_ecdh_cls_guess(m)
                p = cls(m, tls_session=s)
                if pkcs_os2ip(p.load[:2]) not in _tls_hash_sig:
                    return None, Raw(m[:tmp_len]) / Padding(m[tmp_len:])
                return p