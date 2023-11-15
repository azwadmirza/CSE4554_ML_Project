    def __init__(self, hs):
        self.store = hs.get_datastore()
        self.federation = hs.get_federation_client()
        self.device_handler = hs.get_device_handler()
        self.is_mine = hs.is_mine
        self.clock = hs.get_clock()

        self._edu_updater = SigningKeyEduUpdater(hs, self)

        self._is_master = hs.config.worker_app is None
        if not self._is_master:
            self._user_device_resync_client = ReplicationUserDevicesResyncRestServlet.make_client(
                hs
            )

        federation_registry = hs.get_federation_registry()

        # FIXME: switch to m.signing_key_update when MSC1756 is merged into the spec
        federation_registry.register_edu_handler(
            "org.matrix.signing_key_update",
            self._edu_updater.incoming_signing_key_update,
        )
        # doesn't really work as part of the generic query API, because the
        # query request requires an object POST, but we abuse the
        # "query handler" interface.
        federation_registry.register_query_handler(
            "client_keys", self.on_federation_query_client_keys
        )