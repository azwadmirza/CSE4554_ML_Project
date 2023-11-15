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