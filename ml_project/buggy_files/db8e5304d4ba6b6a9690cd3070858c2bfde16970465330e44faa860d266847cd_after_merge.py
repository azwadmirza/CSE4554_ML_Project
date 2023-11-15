    def DisplayPasskey(self, device, passkey, entered):
        dprint('DisplayPasskey (%s, %d)' % (device, passkey))
        notify_message = _("Pairing passkey for") + " %s: %s" % (self.get_device_alias(device), passkey)
        self.n = Notification("Bluetooth", notify_message, 0,
                              pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)