        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                ret = pin_entry.get_text()
                if is_numeric:
                    ret = GLib.Variant('(u)', int(ret))
                ok(ret)
            else:
                err(BluezErrorRejected("Rejected"))
            dialog.destroy()
            self.dialog = None