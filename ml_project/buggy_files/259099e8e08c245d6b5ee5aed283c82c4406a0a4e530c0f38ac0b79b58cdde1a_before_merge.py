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
        email = config.get(CONF_EMAIL)
        login_obj = hass.data[DATA_ALEXAMEDIA]["accounts"][email]["login_obj"]
        if (
            email not in hass.data[DATA_ALEXAMEDIA]["accounts"]
            or not login_obj.status.get("login_successful")
            or login_obj.session.closed
            or login_obj.close_requested
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
        ]
        if new_devices:
            tasks.append(AlexaAPI.get_authentication(login_obj))

        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(30):
                if new_devices:
                    (
                        devices,
                        bluetooth,
                        preferences,
                        dnd,
                        auth_info,
                    ) = await asyncio.gather(*tasks)
                else:
                    (devices, bluetooth, preferences, dnd,) = await asyncio.gather(
                        *tasks
                    )
                _LOGGER.debug(
                    "%s: Found %s devices, %s bluetooth",
                    hide_email(email),
                    len(devices) if devices is not None else "",
                    len(bluetooth.get("bluetoothStates", []))
                    if bluetooth is not None
                    else "",
                )
        except (AlexapyLoginError, JSONDecodeError):
            _LOGGER.debug(
                "%s: Alexa API disconnected; attempting to relogin : status %s",
                hide_email(email),
                login_obj.status,
            )
            if login_obj.status:
                hass.bus.async_fire(
                    "alexa_media_relogin_required",
                    event_data={"email": hide_email(email), "url": login_obj.url},
                )
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
            if exclude and dev_name in exclude:
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

            if (
                dev_name not in include_filter
                and device.get("capabilities")
                and not any(
                    x in device["capabilities"]
                    for x in ["MUSIC_SKILL", "TIMERS_AND_ALARMS", "REMINDERS"]
                )
            ):
                # skip devices without music or notification skill
                _LOGGER.debug("Excluding %s for lacking capability", dev_name)
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
            elif (
                serial in existing_serials
                and hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][
                    "media_player"
                ].get(serial)
                and hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][
                    "media_player"
                ]
                .get(serial)
                .enabled
            ):
                await hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][
                    "media_player"
                ].get(serial).refresh(device, skip_api=True)
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
                entry_setup = len(
                    hass.data[DATA_ALEXAMEDIA]["accounts"][email]["entities"][component]
                )
                if not entry_setup:
                    _LOGGER.debug("Loading config entry for %s", component)
                    hass.async_add_job(
                        hass.config_entries.async_forward_entry_setup(
                            config_entry, component
                        )
                    )
                else:
                    _LOGGER.debug("Loading %s", component)
                    hass.async_create_task(
                        async_load_platform(
                            hass,
                            component,
                            DOMAIN,
                            {CONF_NAME: DOMAIN, "config": cleaned_config},
                            cleaned_config,
                        )
                    )

        hass.data[DATA_ALEXAMEDIA]["accounts"][email]["new_devices"] = False
        await login_obj.save_cookiefile()
        if login_obj.access_token:
            hass.config_entries.async_update_entry(
                config_entry,
                data={
                    **config_entry.data,
                    CONF_OAUTH: {
                        "access_token": login_obj.access_token,
                        "refresh_token": login_obj.refresh_token,
                        "expires_in": login_obj.expires_in,
                    },
                },
            )