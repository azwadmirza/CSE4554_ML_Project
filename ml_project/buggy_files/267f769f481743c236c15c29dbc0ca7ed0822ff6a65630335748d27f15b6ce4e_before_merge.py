    def render_GET(self, _):
        """
        .. http:get:: /channels/subscribed

        Returns all the channels the user is subscribed to.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/channels/subscribed

            **Example response**:

            .. sourcecode:: javascript

                {
                    "subscribed": [{
                        "id": 3,
                        "dispersy_cid": "da69aaad39ccf468aba2ab9177d5f8d8160135e6",
                        "name": "My fancy channel",
                        "description": "A description of this fancy channel",
                        "subscribed": True,
                        "votes": 23,
                        "torrents": 3,
                        "spam": 5,
                        "modified": 14598395,
                        "can_edit": True,
                    }, ...]
                }
        """
        subscribed_channels_db = self.channel_db_handler.getMySubscribedChannels(include_dispersy=True)
        results_json = [convert_db_channel_to_json(channel) for channel in subscribed_channels_db]
        return json.dumps({"subscribed": results_json})