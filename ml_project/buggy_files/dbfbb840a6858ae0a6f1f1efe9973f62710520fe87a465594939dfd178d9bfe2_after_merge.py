        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                ret = pin_entry.get_text()
                ok(int(ret) if is_numeric else ret)
            else:
                err(BluezErrorRejected("Rejected"))
            dialog.destroy()
            self.dialog = None