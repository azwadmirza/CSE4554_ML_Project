        def _on_loaded(response):
            if response.startswith(b'magnet'):
                _, infohash, _ = parse_magnetlink(response)
                if infohash:
                    self.session.lm.ltmgr.get_metainfo(infohash, timeout=20).addCallback(on_got_metainfo)
                    return

            # Otherwise, we directly invoke the on_got_metainfo method
            try:
                decoded_response = bdecode_compat(response)
                on_got_metainfo(decoded_response)
            except RuntimeError:
                # The decoding failed - handle it like a None metainfo
                on_got_metainfo(None)