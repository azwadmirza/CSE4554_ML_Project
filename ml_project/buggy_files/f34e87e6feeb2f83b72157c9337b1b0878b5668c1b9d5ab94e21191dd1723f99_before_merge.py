    def create_introduction_point(self, info_hash, amount=1):
        download = self.get_download(info_hash)
        if download:
            # We now have to associate the SOCKS5 UDP connection with the libtorrent listen port ourselves.
            # The reason for this is that libtorrent does not include the source IP/port in an SOCKS5 ASSOCIATE message.
            # In libtorrent < 1.2.0, we could do so by simply adding an (invalid) peer to the download to enforce
            # an outgoing message through the SOCKS5 port.
            # This does not seem to work anymore in libtorrent 1.2.0 (and probably higher) so we manually associate
            # the connection and the libtorrent listen port.
            if LooseVersion(self.tribler_session.lm.ltmgr.get_libtorrent_version()) < LooseVersion("1.2.0"):
                download.add_peer(('1.1.1.1', 1024))
            else:
                hops = download.config.get_hops()
                lt_listen_port = self.tribler_session.lm.ltmgr.get_session(hops).listen_port()
                for session in self.socks_servers[hops - 1].sessions:
                    session.get_udp_socket().remote_udp_address = ("127.0.0.1", lt_listen_port)
        super(TriblerTunnelCommunity, self).create_introduction_point(info_hash, amount)