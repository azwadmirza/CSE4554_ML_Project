    def load_communities(self):
        self._logger.info("tribler: Preparing communities...")
        now_time = timemod.time()
        default_kwargs = {'tribler_session': self.session}

        # Search Community
        if self.session.get_enable_torrent_search():
            from Tribler.community.search.community import SearchCommunity
            self.dispersy.define_auto_load(SearchCommunity, self.session.dispersy_member, load=True,
                                           kargs=default_kwargs)

        # AllChannel Community
        if self.session.get_enable_channel_search():
            from Tribler.community.allchannel.community import AllChannelCommunity
            self.dispersy.define_auto_load(AllChannelCommunity, self.session.dispersy_member, load=True,
                                           kargs=default_kwargs)

        # Channel Community
        if self.session.get_channel_community_enabled():
            from Tribler.community.channel.community import ChannelCommunity
            self.dispersy.define_auto_load(ChannelCommunity,
                                           self.session.dispersy_member, load=True, kargs=default_kwargs)

        # PreviewChannel Community
        if self.session.get_preview_channel_community_enabled():
            from Tribler.community.channel.preview import PreviewChannelCommunity
            self.dispersy.define_auto_load(PreviewChannelCommunity,
                                           self.session.dispersy_member, kargs=default_kwargs)

        if self.session.get_tunnel_community_enabled():
            tunnel_settings = TunnelSettings(tribler_session=self.session)
            tunnel_kwargs = {'tribler_session': self.session, 'settings': tunnel_settings}

            if self.session.get_enable_multichain():
                multichain_kwargs = {'tribler_session': self.session}

                # If the multichain is enabled, we use the permanent multichain keypair
                # for both the multichain and the tunnel community
                keypair = self.session.multichain_keypair
                dispersy_member = self.dispersy.get_member(private_key=keypair.key_to_bin())

                from Tribler.community.multichain.community import MultiChainCommunity
                self.dispersy.define_auto_load(MultiChainCommunity,
                                               dispersy_member,
                                               load=True,
                                               kargs=multichain_kwargs)

            else:
                keypair = self.dispersy.crypto.generate_key(u"curve25519")
                dispersy_member = self.dispersy.get_member(private_key=self.dispersy.crypto.key_to_bin(keypair))

            from Tribler.community.tunnel.hidden_community import HiddenTunnelCommunity
            self.tunnel_community = self.dispersy.define_auto_load(HiddenTunnelCommunity, dispersy_member,
                                                                   load=True, kargs=tunnel_kwargs)[0]

            # We don't want to automatically load other instances of this community with other master members.
            self.dispersy.undefine_auto_load(HiddenTunnelCommunity)

        self._logger.info("tribler: communities are ready in %.2f seconds", timemod.time() - now_time)