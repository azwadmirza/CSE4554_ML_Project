    def ws_close_handler():
        """Handle websocket close.

        This should attempt to reconnect.
        """
        email = login_obj.email
        _LOGGER.debug("%s: Received websocket close; attempting reconnect",
                      hide_email(email))
        (hass.data[DATA_ALEXAMEDIA]['accounts'][email]['websocket']) = ws_connect()