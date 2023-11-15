    def __init__(self, hs):
        super(GenericWorkerReplicationHandler, self).__init__(hs)

        self.store = hs.get_datastore()
        self.typing_handler = hs.get_typing_handler()
        self.presence_handler = hs.get_presence_handler()  # type: GenericWorkerPresence
        self.notifier = hs.get_notifier()

        self.notify_pushers = hs.config.start_pushers
        self.pusher_pool = hs.get_pusherpool()

        self.send_handler = None  # type: Optional[FederationSenderHandler]
        if hs.config.send_federation:
            self.send_handler = FederationSenderHandler(hs)