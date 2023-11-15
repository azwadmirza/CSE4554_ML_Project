    async def start_notify(
        self, _uuid: str, callback: Callable[[str, Any], Any], **kwargs
    ) -> None:
        """Activate notifications/indications on a characteristic.

        Callbacks must accept two inputs. The first will be a uuid string
        object and the second will be a bytearray.

        .. code-block:: python

            def callback(sender, data):
                print(f"{sender}: {data}")
            client.start_notify(char_uuid, callback)

        Args:
            _uuid (str or UUID): The uuid of the characteristics to start notification on.
            callback (function): The function to be called on notification.

        Keyword Args:
            notification_wrapper (bool): Set to `False` to avoid parsing of
                notification to bytearray.

        """

        _wrap = kwargs.get("notification_wrapper", True)
        characteristic = self.services.get_characteristic(str(_uuid))
        await self._bus.callRemote(
            characteristic.path,
            "StartNotify",
            interface=defs.GATT_CHARACTERISTIC_INTERFACE,
            destination=defs.BLUEZ_SERVICE,
            signature="",
            body=[],
            returnSignature="",
        ).asFuture(self.loop)

        if _wrap:
            self._notification_callbacks[
                characteristic.path
            ] = _data_notification_wrapper(
                callback, self._char_path_to_uuid
            )  # noqa | E123 error in flake8...
        else:
            self._notification_callbacks[
                characteristic.path
            ] = _regular_notification_wrapper(
                callback, self._char_path_to_uuid
            )  # noqa | E123 error in flake8...