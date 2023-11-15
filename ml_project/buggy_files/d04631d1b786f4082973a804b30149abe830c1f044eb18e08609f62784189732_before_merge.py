    def __init__(self, config, flow, event_queue, should_exit):
        """
            event_queue can be a queue or None, if no scripthooks should be
            processed.
        """
        self.config, self.flow = config, flow
        if event_queue:
            self.channel = controller.Channel(event_queue, should_exit)
        else:
            self.channel = None
        super(RequestReplayThread, self).__init__(
            "RequestReplay (%s)" % flow.request.url
        )