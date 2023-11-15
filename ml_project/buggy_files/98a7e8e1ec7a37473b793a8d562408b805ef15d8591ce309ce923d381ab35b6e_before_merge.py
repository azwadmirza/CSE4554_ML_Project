        def _on_success(_):
            with db_session:
                channel_upd = self.session.lm.mds.ChannelMetadata.get(public_key=channel.public_key, id_=channel.id_)
                channel_upd_dict = channel_upd.to_simple_dict()
            self.session.notifier.notify(NTFY_CHANNEL_ENTITY, NTFY_UPDATE,
                                         "%s:%s".format(hexlify(channel.public_key), str(channel.id_)),
                                         channel_upd_dict)