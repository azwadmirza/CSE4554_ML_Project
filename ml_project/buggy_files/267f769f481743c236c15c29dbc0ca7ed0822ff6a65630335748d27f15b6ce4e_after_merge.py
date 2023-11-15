    def render_GET(self, request):
        """
        .. http:get:: /channels/subscribed/(string: channelid)

        Shows the status of subscription to a specific channel along with number of existing votes in the channel

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/channels/subscribed/da69aaad39ccf468aba2ab9177d5f8d8160135e6

            **Example response**:

            .. sourcecode:: javascript

                {
                    "subscribed" : True, "votes": 111
                }
        """
        request.setHeader('Content-Type', 'text/json')
        channel_info = self.get_channel_from_db(self.cid)

        if channel_info is None:
            return ChannelsModifySubscriptionEndpoint.return_404(request)

        response = dict()
        response[u'subscribed'] = channel_info[7] == VOTE_SUBSCRIBE
        response[u'votes'] = channel_info[5]

        return json.dumps(response)