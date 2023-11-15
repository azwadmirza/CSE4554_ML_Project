    def connect(self, **kwargs):
        """Connect to the device."""
        super().connect()
        try:
            self._open()
        except usb.core.USBError as err:
            LOGGER.warning('report: failed to open right away, will close first')
            LOGGER.debug(err, exc_info=True)
            self._close()
            self._open()
        finally:
            self.device.release()