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