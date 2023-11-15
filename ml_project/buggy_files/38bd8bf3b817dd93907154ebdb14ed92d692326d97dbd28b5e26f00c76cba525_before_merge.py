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