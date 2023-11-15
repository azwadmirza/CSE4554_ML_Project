    def perform_query(self, **kwargs):
        if "rest_endpoint_url" not in kwargs:
            kwargs.update({
                "rest_endpoint_url": "metadata/channels/%s/%i/torrents" % (self.model.channel_pk,
                                                                           self.model.channel_id)})
        super(TorrentsTableViewController, self).perform_query(**kwargs)