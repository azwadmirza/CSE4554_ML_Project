    def render_GET(self, request):
        """
        .. http:get:: /libtorrent/settings

        A GET request to this endpoint will return information about libtorrent.

            **Example request**:

                .. sourcecode:: none

                    curl -X GET http://localhost:8085/libtorrent/settings?hop=0

            **Example response**:

                .. sourcecode:: javascript

                    {
                        "hop": 0,
                        "settings": {
                            "urlseed_wait_retry": 30,
                            "enable_upnp": true,
                            ...
                            "send_socket_buffer_size": 0,
                            "lock_disk_cache": false,
                            "i2p_port": 0
                        }
                    }
        """
        args = recursive_unicode(request.args)
        hop = 0
        if 'hop' in args and args['hop']:
            hop = int(args['hop'][0])

        if hop not in self.session.lm.ltmgr.ltsessions:
            return json.twisted_dumps({'hop': hop, "settings": {}})

        lt_session = self.session.lm.ltmgr.ltsessions[hop]
        if hop == 0:
            lt_settings = self.session.lm.ltmgr.ltsettings[lt_session]
            lt_settings['peer_fingerprint'] = hexlify(lt_settings['peer_fingerprint'])
        else:
            lt_settings = lt_session.get_settings()

        return json.twisted_dumps({'hop': hop, "settings": lt_settings})