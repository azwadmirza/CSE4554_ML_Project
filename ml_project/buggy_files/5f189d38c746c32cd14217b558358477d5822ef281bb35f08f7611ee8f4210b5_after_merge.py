    def start(  # type: ignore
        self,
        raiden_service: "RaidenService",
        whitelist: List[Address],
        prev_auth_data: Optional[str],
    ) -> None:
        if not self._stop_event.ready():
            raise RuntimeError(f"{self!r} already started")
        self.log.debug("Matrix starting")
        self._stop_event.clear()
        self._starting = True
        self._raiden_service = raiden_service

        self._address_mgr.start()

        try:
            login(
                client=self._client,
                signer=self._raiden_service.signer,
                prev_auth_data=prev_auth_data,
            )
        except ValueError:
            # `ValueError` may be raised if `get_user` provides invalid data to
            # the `User` constructor. This is either a bug in the login, that
            # tries to get the user after a failed login, or a bug in the
            # Matrix SDK.
            raise RaidenUnrecoverableError("Matrix SDK failed to properly set the userid")
        except MatrixHttpLibError:
            raise RaidenUnrecoverableError("The Matrix homeserver seems to be unavailable.")

        self.log = log.bind(
            current_user=self._user_id,
            node=to_checksum_address(self._raiden_service.address),
            transport_uuid=str(self._uuid),
        )

        self._initialize_first_sync()
        self._initialize_broadcast_rooms()
        self._initialize_room_inventory()

        def on_success(greenlet: gevent.Greenlet) -> None:
            if greenlet in self.greenlets:
                self.greenlets.remove(greenlet)

        self._client.start_listener_thread()
        assert isinstance(self._client.sync_thread, gevent.Greenlet)
        self._client.sync_thread.link_exception(self.on_error)
        self._client.sync_thread.link_value(on_success)
        self.greenlets = [self._client.sync_thread]

        self._client.set_presence_state(UserPresence.ONLINE.value)

        # (re)start any _RetryQueue which was initialized before start
        for retrier in self._address_to_retrier.values():
            if not retrier:
                self.log.debug("Starting retrier", retrier=retrier)
                retrier.start()

        super().start()  # start greenlet
        self._starting = False
        self._started = True

        pool = Pool(size=10)
        greenlets = set(pool.apply_async(self.whitelist, [address]) for address in whitelist)
        gevent.joinall(greenlets, raise_error=True)

        self.log.debug("Matrix started", config=self._config)

        # Handle any delayed invites in the future
        self._schedule_new_greenlet(self._process_queued_invites, in_seconds_from_now=1)