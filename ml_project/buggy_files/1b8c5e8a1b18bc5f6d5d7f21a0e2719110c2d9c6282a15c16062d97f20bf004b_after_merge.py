    def ask_passkey(self, dialog_msg, notify_msg, is_numeric, notification, device_path, ok, err):
        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                ret = pin_entry.get_text()
                ok(int(ret) if is_numeric else ret)
            else:
                err(BluezErrorRejected("Rejected"))
            dialog.destroy()
            self.dialog = None

        dev_str = self.get_device_string(device_path)
        notify_message = _("Pairing request for %s") % dev_str

        if self.dialog:
            logging.info("Agent: Another dialog still active, cancelling")
            err(BluezErrorCanceled("Canceled"))

        self.dialog, pin_entry = self.build_passkey_dialog(dev_str, dialog_msg, is_numeric)
        if not self.dialog:
            logging.error("Agent: Failed to build dialog")
            err(BluezErrorCanceled("Canceled"))

        if notification:
            Notification(_("Bluetooth Authentication"), notify_message, icon_name="blueman").show()

        self.dialog.connect("response", passkey_dialog_cb)
        self.dialog.present()