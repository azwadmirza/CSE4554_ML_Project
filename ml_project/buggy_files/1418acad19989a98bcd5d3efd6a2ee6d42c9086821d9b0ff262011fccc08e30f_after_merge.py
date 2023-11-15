    def render_POST(self, request):
        parameters = recursive_unicode(http.parse_qs(request.content.read(), 1))
        if 'subscribe' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.twisted_dumps({"success": False, "error": "subscribe parameter missing"})

        to_subscribe = int(parameters['subscribe'][0]) == 1
        with db_session:
            channel = self.session.lm.mds.ChannelMetadata.get_for_update(public_key=database_blob(self.channel_pk),
                                                                         id_=self.channel_id)
            if not channel:
                request.setResponseCode(http.NOT_FOUND)
                return json.twisted_dumps({"error": "this channel cannot be found"})

            if channel.status == LEGACY_ENTRY:
                return json.twisted_dumps({"error": "Cannot subscribe to a legacy channel"})

            channel.subscribed = to_subscribe
            channel.share = to_subscribe
            if not to_subscribe:
                channel.local_version = 0
            channel_state = channel.to_simple_dict()["state"]

        def delete_channel():
            # TODO: this should be eventually moved to a garbage-collector-like subprocess in MetadataStore
            with db_session:
                channel = self.session.lm.mds.ChannelMetadata.get_for_update(public_key=database_blob(self.channel_pk),
                                                                             id_=self.channel_id)
                contents = channel.contents
                contents.delete(bulk=True)
            self.session.lm.mds._db.disconnect()

        if not to_subscribe:
            reactor.callInThread(delete_channel)

        return json.twisted_dumps({"success": True, "subscribed": to_subscribe, "state": channel_state})