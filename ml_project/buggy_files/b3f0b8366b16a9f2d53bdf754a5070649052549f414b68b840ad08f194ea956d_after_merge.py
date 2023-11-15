    def perform_query(self, **kwargs):
        # On some systems, URLs containing double slashes are handled incorrectly.
        # To circumvent this limitation, for empty public key we use a special substitute
        if "rest_endpoint_url" not in kwargs:
            kwargs.update({
                "rest_endpoint_url": "metadata/channels/%s/%i/torrents" %
                                     (self.model.channel_pk,
                                      self.model.channel_id)})
        super(TorrentsTableViewController, self).perform_query(**kwargs)