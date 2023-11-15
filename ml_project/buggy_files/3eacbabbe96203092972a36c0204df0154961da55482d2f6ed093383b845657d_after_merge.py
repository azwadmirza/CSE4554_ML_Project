    def disconnect(self, **kwargs):
        """Disconnect from the device.

        Implementation note: unlike SI_Close is supposed to do,¹ do not send
        _USBXPRESS_NOT_CLEAR_TO_SEND to the device.  This allows one program to
        disconnect without sotping reads from another.

        Surrounding device.read() with _USBXPRESS_[NOT_]CLEAR_TO_SEND would
        make more sense, but there seems to be a yet unknown minimum delay
        necessary for that to work well.

        ¹ https://github.com/craigshelley/SiUSBXp/blob/master/SiUSBXp.c
        """
        super().disconnect(**kwargs)