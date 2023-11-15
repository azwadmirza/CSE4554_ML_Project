    def on_subscription_status(self, source_address, data):
        """
        Message handler for content subscription message. Content subscription message is sent by the publisher stating
        the status of the subscription in response to subscribe or unsubscribe request.

        If the subscription message has subscribe=True, it means the subscription was successful, so the peer is added
        to the subscriber. In other case, publisher is removed if it is still present in the publishers list.
        """
        auth, _, payload = self._ez_unpack_auth(ContentSubscription, data)
        peer = self.get_peer_from_auth(auth, source_address)

        if not self.request_cache.has(u'request', payload.identifier):
            return
        self.request_cache.pop(u'request', payload.identifier)

        if payload.subscribe:
            self.publishers.add(peer)
        elif peer in self.publishers:
            self.publishers.remove(peer)