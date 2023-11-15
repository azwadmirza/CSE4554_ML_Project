    def __init__(self, channel, ttyBaudrate=115200, timeout=1, bitrate=None, **kwargs):
        """
        :param str channel:
            port of underlying serial or usb device (e.g. /dev/ttyUSB0, COM8, ...)
            Must not be empty.
        :param int ttyBaudrate:
            baudrate of underlying serial or usb device
        :param int bitrate:
            Bitrate in bit/s
        :param float poll_interval:
            Poll interval in seconds when reading messages
        :param float timeout:
            timeout in seconds when reading message
        """

        if not channel: # if None or empty
            raise TypeError("Must specify a serial port.")

        if '@' in channel:
            (channel, ttyBaudrate) = channel.split('@')

        self.serialPortOrig = serial.Serial(channel, baudrate=ttyBaudrate, timeout=timeout)

        time.sleep(self._SLEEP_AFTER_SERIAL_OPEN)

        if bitrate is not None:
            self.close()
            if bitrate in self._BITRATES:
                self.write(self._BITRATES[bitrate])
            else:
                raise ValueError("Invalid bitrate, choose one of " + (', '.join(self._BITRATES)) + '.')

        self.open()

        super(slcanBus, self).__init__(channel, ttyBaudrate=115200, timeout=1,
                                       bitrate=None, **kwargs)