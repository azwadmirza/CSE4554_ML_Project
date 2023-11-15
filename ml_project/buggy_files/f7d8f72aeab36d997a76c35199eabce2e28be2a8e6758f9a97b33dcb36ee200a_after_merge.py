    def render_POST(self, request):
        """
        .. http:post:: /channels/discovered/(string: channelid)/recheckfeeds

        Rechecks all rss feeds in your channel. Returns error 404 if you channel does not exist.

            **Example request**:

            .. sourcecode:: none

                curl -X POST http://localhost:8085/channels/discovered/recheckrssfeeds

            **Example response**:

            .. sourcecode:: javascript

                {
                    "rechecked": True
                }

            :statuscode 404: if you have not created a channel.
        """
        channel_obj, error = self.get_my_channel_obj_or_error(request)
        if channel_obj is None:
            return error

        def on_refreshed(_):
            request.write(json.dumps({"rechecked": True}))
            request.finish()

        def on_refresh_error(failure):
            self._logger.exception(failure.value)
            request.write(BaseChannelsEndpoint.return_500(self, request, failure.value))
            request.finish()

        channel_obj.refresh_all_feeds().addCallbacks(on_refreshed, on_refresh_error)

        return NOT_DONE_YET