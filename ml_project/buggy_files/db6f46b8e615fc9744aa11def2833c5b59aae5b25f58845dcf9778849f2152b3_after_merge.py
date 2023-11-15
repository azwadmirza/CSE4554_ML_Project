    def DisplayPinCode(self, device, pin_code):
        dprint('DisplayPinCode (%s, %s)' % (device, pin_code))
        notify_message = _("Pairing PIN code for") + " %s: %s" % (self.get_device_alias(device), pin_code)
        self.n = Notification("Bluetooth", notify_message, 0,
                              pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)