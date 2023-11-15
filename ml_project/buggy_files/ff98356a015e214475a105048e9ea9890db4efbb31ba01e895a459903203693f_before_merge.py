async def setup_alexa(hass, config_entry, login_obj):
    """Set up a alexa api based on host parameter."""

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.

        This will ping Alexa API to identify all devices, bluetooth, and the last
        called device.

        This will add new devices and services when discovered. By default this
        runs every SCAN_INTERVAL seconds unless another method calls it. if
        websockets is connected, it will increase the delay 10-fold between updates.
        While throttled at MIN_TIME_BETWEEN_SCANS, care should be taken to
        reduce the number of runs to avoid flooding. Slow changing states
        should be checked here instead of in spawned components like
        media_player since this object is one per account.
        Each AlexaAPI call generally results in two webpage requests.
        """
        from alexapy import AlexaAPI

        email: Text = login_obj.email
        if (
            email not in hass.data[DATA_ALEXAMEDIA]["accounts"]
            or "login_successful" not in login_obj.status
        ):
            return
        existing_serials = _existing_serials(hass, login_obj)
        existing_entities = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][
            "media_player"
        ].values()
        auth_info = hass.data[DATA_ALEXAMEDIA]["accounts"][email].get("auth_info")
        new_devices = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["new_devices"]
        devices = {}
        bluetooth = {}
        preferences = {}
        dnd = {}
        raw_notifications = {}
        tasks = [
            AlexaAPI.get_devices(login_obj),
            AlexaAPI.get_bluetooth(login_obj),
            AlexaAPI.get_device_preferences(login_obj),
            AlexaAPI.get_dnd_state(login_obj),
            AlexaAPI.get_notifications(login_obj),
        ]
        if new_devices:
            tasks.append(AlexaAPI.get_authentication(login_obj))

        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                if new_devices:
                    (
                        devices,
                        bluetooth,
                        preferences,
                        dnd,
                        raw_notifications,
                        auth_info,
                    ) = await asyncio.gather(*tasks)
                else:
                    (
                        devices,
                        bluetooth,
                        preferences,
                        dnd,
                        raw_notifications,
                    ) = await asyncio.gather(*tasks)
                _LOGGER.debug(
                    "%s: Found %s devices, %s bluetooth",
                    hide_email(email),
                    len(devices) if devices is not None else "",
                    len(bluetooth.get("bluetoothStates", []))
                    if bluetooth is not None
                    else "",
                )
                if (devices is None or bluetooth is None) and not (
                    hass.data[DATA_ALEXAMEDIA]["accounts"][email]["configurator"]
                ):
                    raise AlexapyLoginError()
        except (AlexapyLoginError, JSONDecodeError):
            _LOGGER.debug(
                "%s: Alexa API disconnected; attempting to relogin : status %s",
                hide_email(email),
                login_obj.status,
            )
            if login_obj.status and not await test_login_status(
                hass, config_entry, login_obj, setup_alexa
            ):
                login_obj.status = {}
                await login_obj.login()
            return
        except BaseException as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

        await process_notifications(login_obj, raw_notifications)
        # Process last_called data to fire events
        await update_last_called(login_obj)

        new_alexa_clients = []  # list of newly discovered device names
        exclude_filter = []
        include_filter = []

        for device in devices:
            serial = device["serialNumber"]
            dev_name = device["accountName"]
            if include and dev_name not in include:
                include_filter.append(dev_name)
                if "appDeviceList" in device:
                    for app in device["appDeviceList"]:
                        (
                            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["excluded"][
                                app["serialNumber"]
                            ]
                        ) = device
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["excluded"][
                    serial
                ] = device
                continue
            elif exclude and dev_name in exclude:
                exclude_filter.append(dev_name)
                if "appDeviceList" in device:
                    for app in device["appDeviceList"]:
                        (
                            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["excluded"][
                                app["serialNumber"]
                            ]
                        ) = device
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["excluded"][
                    serial
                ] = device
                continue

            if "bluetoothStates" in bluetooth:
                for b_state in bluetooth["bluetoothStates"]:
                    if serial == b_state["deviceSerialNumber"]:
                        device["bluetooth_state"] = b_state
                        break

            if "devicePreferences" in preferences:
                for dev in preferences["devicePreferences"]:
                    if dev["deviceSerialNumber"] == serial:
                        device["locale"] = dev["locale"]
                        device["timeZoneId"] = dev["timeZoneId"]
                        _LOGGER.debug(
                            "%s: Locale %s timezone %s",
                            dev_name,
                            device["locale"],
                            device["timeZoneId"],
                        )
                        break

            if "doNotDisturbDeviceStatusList" in dnd:
                for dev in dnd["doNotDisturbDeviceStatusList"]:
                    if dev["deviceSerialNumber"] == serial:
                        device["dnd"] = dev["enabled"]
                        _LOGGER.debug("%s: DND %s", dev_name, device["dnd"])
                        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["devices"][
                            "switch"
                        ].setdefault(serial, {"dnd": True})

                        break
            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["auth_info"] = device[
                "auth_info"
            ] = auth_info
            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["devices"]["media_player"][
                serial
            ] = device

            if serial not in existing_serials:
                new_alexa_clients.append(dev_name)
            elif serial in existing_entities:
                await hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][
                    "media_player"
                ].get(serial).refresh(device, no_api=True)
        _LOGGER.debug(
            "%s: Existing: %s New: %s;"
            " Filtered out by not being in include: %s "
            "or in exclude: %s",
            hide_email(email),
            list(existing_entities),
            new_alexa_clients,
            include_filter,
            exclude_filter,
        )

        if new_alexa_clients:
            cleaned_config = config.copy()
            cleaned_config.pop(CONF_PASSWORD, None)
            # CONF_PASSWORD contains sensitive info which is no longer needed
            for component in ALEXA_COMPONENTS:
                _LOGGER.debug("Loading %s", component)
                hass.async_add_job(
                    hass.config_entries.async_forward_entry_setup(
                        config_entry, component
                    )
                )

        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["new_devices"] = False

    async def process_notifications(login_obj, raw_notifications=None):
        """Process raw notifications json."""
        from alexapy import AlexaAPI

        if not raw_notifications:
            raw_notifications = await AlexaAPI.get_notifications(login_obj)
        email: Text = login_obj.email
        notifications = {"process_timestamp": datetime.utcnow()}
        for notification in raw_notifications:
            n_dev_id = notification.get("deviceSerialNumber")
            if n_dev_id is None:
                # skip notifications untied to a device for now
                # https://github.com/custom-components/alexa_media_player/issues/633#issuecomment-610705651
                continue
            n_type = notification.get("type")
            if n_type is None:
                continue
            if n_type == "MusicAlarm":
                n_type = "Alarm"
            n_id = notification["notificationIndex"]
            if n_type == "Alarm":
                n_date = notification.get("originalDate")
                n_time = notification.get("originalTime")
                notification["date_time"] = (
                    f"{n_date} {n_time}" if n_date and n_time else None
                )
            if n_dev_id not in notifications:
                notifications[n_dev_id] = {}
            if n_type not in notifications[n_dev_id]:
                notifications[n_dev_id][n_type] = {}
            notifications[n_dev_id][n_type][n_id] = notification
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["notifications"] = notifications
        _LOGGER.debug(
            "%s: Updated %s notifications for %s devices at %s",
            hide_email(email),
            len(raw_notifications),
            len(notifications),
            dt.as_local(
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["notifications"][
                    "process_timestamp"
                ]
            ),
        )

    async def update_last_called(login_obj, last_called=None):
        """Update the last called device for the login_obj.

        This will store the last_called in hass.data and also fire an event
        to notify listeners.
        """
        from alexapy import AlexaAPI

        if not last_called:
            last_called = await AlexaAPI.get_last_device_serial(login_obj)
        _LOGGER.debug(
            "%s: Updated last_called: %s", hide_email(email), hide_serial(last_called)
        )
        stored_data = hass.data[DATA_ALEXAMEDIA]["accounts"][email]
        if (
            "last_called" in stored_data and last_called != stored_data["last_called"]
        ) or ("last_called" not in stored_data and last_called is not None):
            _LOGGER.debug(
                "%s: last_called changed: %s to %s",
                hide_email(email),
                hide_serial(
                    stored_data["last_called"] if "last_called" in stored_data else None
                ),
                hide_serial(last_called),
            )
            async_dispatcher_send(
                hass,
                f"{DOMAIN}_{hide_email(email)}"[0:32],
                {"last_called_change": last_called},
            )
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["last_called"] = last_called

    async def update_bluetooth_state(login_obj, device_serial):
        """Update the bluetooth state on ws bluetooth event."""
        from alexapy import AlexaAPI

        bluetooth = await AlexaAPI.get_bluetooth(login_obj)
        device = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["devices"][
            "media_player"
        ][device_serial]

        if "bluetoothStates" in bluetooth:
            for b_state in bluetooth["bluetoothStates"]:
                if device_serial == b_state["deviceSerialNumber"]:
                    # _LOGGER.debug("%s: setting value for: %s to %s",
                    #               hide_email(email),
                    #               hide_serial(device_serial),
                    #               hide_serial(b_state))
                    device["bluetooth_state"] = b_state
                    return device["bluetooth_state"]
        _LOGGER.debug(
            "%s: get_bluetooth for: %s failed with %s",
            hide_email(email),
            hide_serial(device_serial),
            hide_serial(bluetooth),
        )
        return None

    async def clear_history(call):
        """Handle clear history service request.

        Arguments
            call.ATTR_EMAIL {List[str: None]} -- Case-sensitive Alexa emails.
                                                 Default is all known emails.
            call.ATTR_NUM_ENTRIES {int: 50} -- Number of entries to delete.

        Returns
            bool -- True if deletion successful

        """
        from alexapy import AlexaAPI

        requested_emails = call.data.get(ATTR_EMAIL)
        items: int = int(call.data.get(ATTR_NUM_ENTRIES))

        _LOGGER.debug(
            "Service clear_history called for: %i items for %s", items, requested_emails
        )
        for email, account_dict in hass.data[DATA_ALEXAMEDIA]["accounts"].items():
            if requested_emails and email not in requested_emails:
                continue
            login_obj = account_dict["login_obj"]
        return await AlexaAPI.clear_history(login_obj, items)

    async def last_call_handler(call):
        """Handle last call service request.

        Args:
        call.ATTR_EMAIL: List of case-sensitive Alexa email addresses. If None
                         all accounts are updated.

        """
        requested_emails = call.data.get(ATTR_EMAIL)
        _LOGGER.debug("Service update_last_called for: %s", requested_emails)
        for email, account_dict in hass.data[DATA_ALEXAMEDIA]["accounts"].items():
            if requested_emails and email not in requested_emails:
                continue
            login_obj = account_dict["login_obj"]
            await update_last_called(login_obj)

    async def ws_connect() -> WebsocketEchoClient:
        """Open WebSocket connection.

        This will only attempt one login before failing.
        """
        websocket: Optional[WebsocketEchoClient] = None
        try:
            websocket = WebsocketEchoClient(
                login_obj,
                ws_handler,
                ws_open_handler,
                ws_close_handler,
                ws_error_handler,
            )
            _LOGGER.debug("%s: Websocket created: %s", hide_email(email), websocket)
            await websocket.async_run()
        except BaseException as exception_:  # pylint: disable=broad-except
            _LOGGER.debug(
                "%s: Websocket creation failed: %s", hide_email(email), exception_
            )
            return
        return websocket

    async def ws_handler(message_obj):
        """Handle websocket messages.

        This allows push notifications from Alexa to update last_called
        and media state.
        """

        command = (
            message_obj.json_payload["command"]
            if isinstance(message_obj.json_payload, dict)
            and "command" in message_obj.json_payload
            else None
        )
        json_payload = (
            message_obj.json_payload["payload"]
            if isinstance(message_obj.json_payload, dict)
            and "payload" in message_obj.json_payload
            else None
        )
        existing_serials = _existing_serials(hass, login_obj)
        seen_commands = hass.data[DATA_ALEXAMEDIA]["accounts"][email][
            "websocket_commands"
        ]
        if command and json_payload:

            _LOGGER.debug(
                "%s: Received websocket command: %s : %s",
                hide_email(email),
                command,
                hide_serial(json_payload),
            )
            serial = None
            if command not in seen_commands:
                seen_commands[command] = time.time()
                _LOGGER.debug("Adding %s to seen_commands: %s", command, seen_commands)
            if (
                "dopplerId" in json_payload
                and "deviceSerialNumber" in json_payload["dopplerId"]
            ):
                serial = json_payload["dopplerId"]["deviceSerialNumber"]
            elif (
                "key" in json_payload
                and "entryId" in json_payload["key"]
                and json_payload["key"]["entryId"].find("#") != -1
            ):
                serial = (json_payload["key"]["entryId"]).split("#")[2]
                json_payload["key"]["serialNumber"] = serial
            else:
                serial = None
            if command == "PUSH_ACTIVITY":
                #  Last_Alexa Updated
                last_called = {
                    "serialNumber": serial,
                    "timestamp": json_payload["timestamp"],
                }
                if serial and serial in existing_serials:
                    await update_last_called(login_obj, last_called)
                async_dispatcher_send(
                    hass,
                    f"{DOMAIN}_{hide_email(email)}"[0:32],
                    {"push_activity": json_payload},
                )
            elif command in (
                "PUSH_AUDIO_PLAYER_STATE",
                "PUSH_MEDIA_CHANGE",
                "PUSH_MEDIA_PROGRESS_CHANGE",
            ):
                # Player update/ Push_media from tune_in
                if serial and serial in existing_serials:
                    _LOGGER.debug(
                        "Updating media_player: %s", hide_serial(json_payload)
                    )
                    async_dispatcher_send(
                        hass,
                        f"{DOMAIN}_{hide_email(email)}"[0:32],
                        {"player_state": json_payload},
                    )
            elif command == "PUSH_VOLUME_CHANGE":
                # Player volume update
                if serial and serial in existing_serials:
                    _LOGGER.debug(
                        "Updating media_player volume: %s", hide_serial(json_payload)
                    )
                    async_dispatcher_send(
                        hass,
                        f"{DOMAIN}_{hide_email(email)}"[0:32],
                        {"player_state": json_payload},
                    )
            elif command in (
                "PUSH_DOPPLER_CONNECTION_CHANGE",
                "PUSH_EQUALIZER_STATE_CHANGE",
            ):
                # Player availability update
                if serial and serial in existing_serials:
                    _LOGGER.debug(
                        "Updating media_player availability %s",
                        hide_serial(json_payload),
                    )
                    async_dispatcher_send(
                        hass,
                        f"{DOMAIN}_{hide_email(email)}"[0:32],
                        {"player_state": json_payload},
                    )
            elif command == "PUSH_BLUETOOTH_STATE_CHANGE":
                # Player bluetooth update
                bt_event = json_payload["bluetoothEvent"]
                bt_success = json_payload["bluetoothEventSuccess"]
                if (
                    serial
                    and serial in existing_serials
                    and bt_success
                    and bt_event
                    and bt_event in ["DEVICE_CONNECTED", "DEVICE_DISCONNECTED"]
                ):
                    _LOGGER.debug(
                        "Updating media_player bluetooth %s", hide_serial(json_payload)
                    )
                    bluetooth_state = await update_bluetooth_state(login_obj, serial)
                    # _LOGGER.debug("bluetooth_state %s",
                    #               hide_serial(bluetooth_state))
                    if bluetooth_state:
                        async_dispatcher_send(
                            hass,
                            f"{DOMAIN}_{hide_email(email)}"[0:32],
                            {"bluetooth_change": bluetooth_state},
                        )
            elif command == "PUSH_MEDIA_QUEUE_CHANGE":
                # Player availability update
                if serial and serial in existing_serials:
                    _LOGGER.debug(
                        "Updating media_player queue %s", hide_serial(json_payload)
                    )
                    async_dispatcher_send(
                        hass,
                        f"{DOMAIN}_{hide_email(email)}"[0:32],
                        {"queue_state": json_payload},
                    )
            elif command == "PUSH_NOTIFICATION_CHANGE":
                # Player update
                await process_notifications(login_obj)
                if serial and serial in existing_serials:
                    _LOGGER.debug(
                        "Updating mediaplayer notifications: %s",
                        hide_serial(json_payload),
                    )
                    async_dispatcher_send(
                        hass,
                        f"{DOMAIN}_{hide_email(email)}"[0:32],
                        {"notification_update": json_payload},
                    )
            elif command in [
                "PUSH_DELETE_DOPPLER_ACTIVITIES",  # delete Alexa history
                "PUSH_LIST_ITEM_CHANGE",  # update shopping list
                "PUSH_CONTENT_FOCUS_CHANGE",  # likely prime related refocus
            ]:
                pass
            else:
                _LOGGER.warning(
                    "Unhandled command: %s with data %s. Please report at %s",
                    command,
                    hide_serial(json_payload),
                    ISSUE_URL,
                )
            if serial in existing_serials:
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocket_activity"][
                    "serials"
                ][serial] = time.time()
            if (
                serial
                and serial not in existing_serials
                and serial
                not in (
                    hass.data[DATA_ALEXAMEDIA]["accounts"][email]["excluded"].keys()
                )
            ):
                _LOGGER.debug("Discovered new media_player %s", serial)
                (hass.data[DATA_ALEXAMEDIA]["accounts"][email]["new_devices"]) = True
                coordinator = hass.data[DATA_ALEXAMEDIA]["accounts"][email].get(
                    "coordinator"
                )
                if coordinator:
                    await coordinator.async_request_refresh()

    async def ws_open_handler():
        """Handle websocket open."""
        import time

        email: Text = login_obj.email
        _LOGGER.debug("%s: Websocket succesfully connected", hide_email(email))
        hass.data[DATA_ALEXAMEDIA]["accounts"][email][
            "websocketerror"
        ] = 0  # set errors to 0
        hass.data[DATA_ALEXAMEDIA]["accounts"][email][
            "websocket_lastattempt"
        ] = time.time()

    async def ws_close_handler():
        """Handle websocket close.

        This should attempt to reconnect up to 5 times
        """
        from asyncio import sleep
        import time

        email: Text = login_obj.email
        errors: int = (hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"])
        delay: int = 5 * 2 ** errors
        last_attempt = hass.data[DATA_ALEXAMEDIA]["accounts"][email][
            "websocket_lastattempt"
        ]
        now = time.time()
        if (now - last_attempt) < delay:
            return
        while errors < 5 and not (
            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocket"]
        ):
            _LOGGER.debug(
                "%s: Websocket closed; reconnect #%i in %is",
                hide_email(email),
                errors,
                delay,
            )
            hass.data[DATA_ALEXAMEDIA]["accounts"][email][
                "websocket_lastattempt"
            ] = time.time()
            hass.data[DATA_ALEXAMEDIA]["accounts"][email][
                "websocket"
            ] = await ws_connect()
            errors = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"] = (
                hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"] + 1
            )
            delay = 5 * 2 ** errors
            await sleep(delay)
            errors = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"]
        _LOGGER.debug(
            "%s: Websocket closed; retries exceeded; polling", hide_email(email)
        )
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocket"] = None
        coordinator = hass.data[DATA_ALEXAMEDIA]["accounts"][email].get("coordinator")
        if coordinator:
            coordinator.update_interval = scan_interval
            await coordinator.async_request_refresh()

    async def ws_error_handler(message):
        """Handle websocket error.

        This currently logs the error.  In the future, this should invalidate
        the websocket and determine if a reconnect should be done. By
        specification, websockets will issue a close after every error.
        """
        email: Text = login_obj.email
        errors = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"]
        _LOGGER.debug(
            "%s: Received websocket error #%i %s: type %s",
            hide_email(email),
            errors,
            message,
            type(message),
        )
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocket"] = None
        if message == "<class 'aiohttp.streams.EofStream'>":
            hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"] = 5
            _LOGGER.debug("%s: Immediate abort on EoFstream", hide_email(email))
            return
        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocketerror"] = errors + 1

    config = config_entry.data
    email = config.get(CONF_EMAIL)
    include = config.get(CONF_INCLUDE_DEVICES)
    exclude = config.get(CONF_EXCLUDE_DEVICES)
    scan_interval: float = (
        config.get(CONF_SCAN_INTERVAL).total_seconds()
        if isinstance(config.get(CONF_SCAN_INTERVAL), timedelta)
        else config.get(CONF_SCAN_INTERVAL)
    )
    hass.data[DATA_ALEXAMEDIA]["accounts"][email]["login_obj"] = login_obj
    websocket_enabled = hass.data[DATA_ALEXAMEDIA]["accounts"][email][
        "websocket"
    ] = await ws_connect()
    coordinator = hass.data[DATA_ALEXAMEDIA]["accounts"][email].get("coordinator")
    if coordinator is None:
        _LOGGER.debug("Creating coordinator")
        hass.data[DATA_ALEXAMEDIA]["accounts"][email][
            "coordinator"
        ] = coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="alexa_media",
            update_method=async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(
                seconds=scan_interval * 10 if websocket_enabled else scan_interval
            ),
        )
    # Fetch initial data so we have data when entities subscribe
    _LOGGER.debug("Refreshing coordinator")
    await coordinator.async_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_LAST_CALLED,
        last_call_handler,
        schema=LAST_CALL_UPDATE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_HISTORY, clear_history, schema=CLEAR_HISTORY_SCHEMA
    )
    # Clear configurator. We delay till here to avoid leaving a modal orphan
    await clear_configurator(hass, email)
    return True