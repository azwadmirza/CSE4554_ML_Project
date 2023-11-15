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