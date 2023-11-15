    async def get_events(self, request):
        """
        .. http:get:: /events

        A GET request to this endpoint will open the event connection.

            **Example request**:

                .. sourcecode:: none

                    curl -X GET http://localhost:52194/events
        """

        # Setting content-type to text/event-stream to ensure browsers will handle the content properly
        response = RESTStreamResponse(status=200,
                                      reason='OK',
                                      headers={'Content-Type': 'text/event-stream',
                                               'Cache-Control': 'no-cache',
                                               'Connection': 'keep-alive'})
        await response.prepare(request)
        # FIXME: Proper start check!
        await response.write(b'data: ' + json.dumps({"type": NTFY.EVENTS_START.value,
                                                     "event": {"tribler_started": self.tribler_started,
                                                               "version": version_id}}).encode('utf-8') + b'\n\n')
        self.events_responses.append(response)
        try:
            while True:
                await self.register_anonymous_task('event_sleep', lambda: None, delay=3600)
        except CancelledError:
            self.events_responses.remove(response)
            return response