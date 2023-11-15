    def __init__(self, session):
        super(GigaChannelManager, self).__init__()
        self.session = session
        self.channels_lc = None

        # We queue up processing of the channels because we do it in a separate thread, and we don't want
        # to run more that one of these simultaneously
        self.channels_processing_queue = []
        self.processing = False