        def _on_loaded(response):
            if response.startswith(b'magnet'):
                _, infohash, _ = parse_magnetlink(response)
                if infohash:
                    self.session.lm.ltmgr.get_metainfo(infohash, timeout=20).addCallback(on_got_metainfo)
                    return

            # Otherwise, we directly invoke the on_got_metainfo method
            on_got_metainfo(bdecode(response))