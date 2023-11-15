def setup_alexa(hass, config, login_obj):
    """Set up a alexa api based on host parameter."""
    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
    def update_devices():
        """Ping Alexa API to identify all devices, bluetooth, and last called device.

        This will add new devices and services when discovered. By default this
        runs every SCAN_INTERVAL seconds unless another method calls it. While
        throttled at MIN_TIME_BETWEEN_SCANS, care should be taken to reduce the
        number of runs to avoid flooding. Slow changing states should be
        checked here instead of in spawned components like media_player since
        this object is one per account.
        Each AlexaAPI call generally results in one webpage request.
        """
        from alexapy import AlexaAPI
        existing_serials = (hass.data[DATA_ALEXAMEDIA]
                            ['accounts']
                            [email]
                            ['entities']
                            ['media_player'].keys())
        existing_entities = (hass.data[DATA_ALEXAMEDIA]
                             ['accounts']
                             [email]
                             ['entities']
                             ['media_player'].values())
        devices = AlexaAPI.get_devices(login_obj)
        bluetooth = AlexaAPI.get_bluetooth(login_obj)
        _LOGGER.debug("%s: Found %s devices, %s bluetooth",
                      hide_email(email),
                      len(devices) if devices is not None else '',
                      len(bluetooth) if bluetooth is not None else '')
        if ((devices is None or bluetooth is None)
                and not hass.data[DOMAIN]['accounts'][email]['config']):
            _LOGGER.debug("Alexa API disconnected; attempting to relogin")
            login_obj.login_with_cookie()
            test_login_status(hass, config, login_obj, setup_platform_callback)
            return

        new_alexa_clients = []  # list of newly discovered device names
        excluded = []
        included = []
        for device in devices:
            if include and device['accountName'] not in include:
                included.append(device['accountName'])
                continue
            elif exclude and device['accountName'] in exclude:
                excluded.append(device['accountName'])
                continue

            for b_state in bluetooth['bluetoothStates']:
                if device['serialNumber'] == b_state['deviceSerialNumber']:
                    device['bluetooth_state'] = b_state

            (hass.data[DATA_ALEXAMEDIA]
             ['accounts']
             [email]
             ['devices']
             ['media_player']
             [device['serialNumber']]) = device

            if device['serialNumber'] not in existing_serials:
                new_alexa_clients.append(device['accountName'])
        _LOGGER.debug("%s: Existing: %s New: %s;"
                      " Filtered by: include_devices: %s exclude_devices:%s",
                      hide_email(email),
                      list(existing_entities),
                      new_alexa_clients,
                      included,
                      excluded)

        if new_alexa_clients:
            for component in ALEXA_COMPONENTS:
                load_platform(hass, component, DOMAIN, {}, config)

        # Process last_called data to fire events
        update_last_called(login_obj)

    def update_last_called(login_obj, last_called=None):
        """Update the last called device for the login_obj.

        This will store the last_called in hass.data and also fire an event
        to notify listeners.
        """
        from alexapy import AlexaAPI
        if last_called:
            last_called = last_called
        else:
            last_called = AlexaAPI.get_last_device_serial(login_obj)
        _LOGGER.debug("%s: Updated last_called: %s",
                      hide_email(email),
                      hide_serial(last_called))
        stored_data = hass.data[DATA_ALEXAMEDIA]['accounts'][email]
        if (('last_called' in stored_data and
             last_called != stored_data['last_called']) or
                ('last_called' not in stored_data and
                 last_called is not None)):
            _LOGGER.debug("%s: last_called changed: %s to %s",
                          hide_email(email),
                          hide_serial(stored_data['last_called'] if
                                      'last_called' in stored_data else None),
                          hide_serial(last_called))
            hass.bus.fire(('{}_{}'.format(DOMAIN, hide_email(email)))[0:32],
                          {'last_called_change': last_called})
        (hass.data[DATA_ALEXAMEDIA]
                  ['accounts']
                  [email]
                  ['last_called']) = last_called

    def last_call_handler(call):
        """Handle last call service request.

        Args:
        call.ATTR_EMAIL: List of case-sensitive Alexa email addresses. If None
                         all accounts are updated.
        """
        requested_emails = call.data.get(ATTR_EMAIL)
        _LOGGER.debug("Service update_last_called for: %s", requested_emails)
        for email, account_dict in (hass.data
                                    [DATA_ALEXAMEDIA]['accounts'].items()):
            if requested_emails and email not in requested_emails:
                continue
            login_obj = account_dict['login_obj']
            update_last_called(login_obj)

    def ws_connect():
        """Open WebSocket connection.

        This will only attempt one login before failing.
        """
        from alexapy import WebsocketEchoClient
        try:
            websocket = WebsocketEchoClient(login_obj,
                                            ws_handler,
                                            ws_close_handler,
                                            ws_error_handler)
            _LOGGER.debug("%s: Websocket created: %s", hide_email(email),
                          websocket)
        except BaseException as exception_:
            _LOGGER.debug("%s: Websocket failed: %s falling back to polling",
                          hide_email(email),
                          exception_)
            websocket = None
        return websocket

    def ws_handler(message_obj):
        """Handle websocket messages.

        This allows push notifications from Alexa to update last_called
        and media state.
        """
        command = (message_obj.json_payload['command']
                   if isinstance(message_obj.json_payload, dict) and
                   'command' in message_obj.json_payload
                   else None)
        json_payload = (message_obj.json_payload['payload']
                        if isinstance(message_obj.json_payload, dict) and
                        'payload' in message_obj.json_payload
                        else None)
        if command and json_payload:
            _LOGGER.debug("%s: Received websocket command: %s : %s",
                          hide_email(email),
                          command, json_payload)
            if command == 'PUSH_ACTIVITY':
                #  Last_Alexa Updated
                last_called = {
                    'serialNumber': (json_payload
                                     ['key']
                                     ['entryId']).split('#')[2],
                    'timestamp': json_payload['timestamp']
                    }
                update_last_called(login_obj, last_called)
            elif command == 'PUSH_AUDIO_PLAYER_STATE':
                # Player update
                _LOGGER.debug("Updating media_player: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_VOLUME_CHANGE':
                # Player volume update
                _LOGGER.debug("Updating media_player volume: %s", json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})
            elif command == 'PUSH_DOPPLER_CONNECTION_CHANGE':
                # Player volume update
                _LOGGER.debug("Updating media_player avalibility %s",
                              json_payload)
                hass.bus.fire(('{}_{}'.format(DOMAIN,
                                              hide_email(email)))[0:32],
                              {'player_state': json_payload})

    def ws_close_handler():
        """Handle websocket close.

        This should attempt to reconnect.
        """
        email = login_obj.email
        _LOGGER.debug("%s: Received websocket close; attempting reconnect",
                      hide_email(email))
        (hass.data[DOMAIN]['accounts'][email]['websocket']) = ws_connect()

    def ws_error_handler(message):
        """Handle websocket error.

        This currently logs the error.  In the future, this should invalidate
        the websocket and determine if a reconnect should be done. By
        specification, websockets will issue a close after every error.
        """
        email = login_obj.email
        _LOGGER.debug("%s: Received websocket error %s",
                      hide_email(email),
                      message)
        (hass.data[DOMAIN]['accounts'][email]['websocket']) = None
    include = config.get(CONF_INCLUDE_DEVICES)
    exclude = config.get(CONF_EXCLUDE_DEVICES)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    email = login_obj.email
    (hass.data[DOMAIN]['accounts'][email]['websocket']) = ws_connect()
    (hass.data[DOMAIN]['accounts'][email]['login_obj']) = login_obj
    (hass.data[DOMAIN]['accounts'][email]['devices']) = {'media_player': {}}
    (hass.data[DOMAIN]['accounts'][email]['entities']) = {'media_player': {}}
    update_devices()
    track_time_interval(hass, lambda now: update_devices(), scan_interval)
    hass.services.register(DOMAIN, SERVICE_UPDATE_LAST_CALLED,
                           last_call_handler, schema=LAST_CALL_UPDATE_SCHEMA)

    # Clear configurator. We delay till here to avoid leaving a modal orphan
    for config_id in hass.data[DOMAIN]['accounts'][email]['config']:
        configurator = hass.components.configurator
        configurator.async_request_done(config_id)
    hass.data[DOMAIN]['accounts'][email]['config'] = []
    return True