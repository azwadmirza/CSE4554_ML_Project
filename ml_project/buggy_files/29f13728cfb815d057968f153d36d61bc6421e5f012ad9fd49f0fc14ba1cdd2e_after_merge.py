    async def is_connected(self) -> bool:
        """Check connection status between this client and the server.

        Returns:
            Boolean representing connection status.

        """
        # TODO: Listen to connected property changes.
        is_connected = False
        try:
            is_connected = await self._bus.callRemote(
                self._device_path,
                "Get",
                interface=defs.PROPERTIES_INTERFACE,
                destination=defs.BLUEZ_SERVICE,
                signature="ss",
                body=[defs.DEVICE_INTERFACE, "Connected"],
                returnSignature="v",
            ).asFuture(asyncio.get_event_loop())
        except AttributeError:
            # The `self._bus` object had already been cleaned up due to disconnect...
            pass
        except ConnectionDone:
            # Twisted error stating that "Connection was closed cleanly."
            pass
        except RemoteError as e:
            if e.errName != 'org.freedesktop.DBus.Error.UnknownObject':
                raise
        except Exception as e:
            # Do not want to silence unknown errors. Send this upwards.
            raise
        return is_connected