    def register_device(self, user_id, device_id=None, initial_display_name=None):
        """Register a device for a user and generate an access token.

        Args:
            user_id (str): full canonical @user:id
            device_id (str|None): The device ID to check, or None to generate
                a new one.
            initial_display_name (str|None): An optional display name for the
                device.

        Returns:
            defer.Deferred[tuple[str, str]]: Tuple of device ID and access token
        """
        return defer.ensureDeferred(
            self._hs.get_registration_handler().register_device(
                user_id=user_id,
                device_id=device_id,
                initial_display_name=initial_display_name,
            )
        )