    def Generate(self):
        self.clear()

        appl = AppletService()

        items = []

        if not self.is_popup or self.props.visible:
            selected = self.Blueman.List.selected()
            if not selected:
                return
            device = self.Blueman.List.get(selected, "device")["device"]
        else:
            (x, y) = self.Blueman.List.get_pointer()
            path = self.Blueman.List.get_path_at_pos(x, y)
            if path != None:
                device = self.Blueman.List.get(path[0], "device")["device"]
            else:
                return

        if not device.Valid:
            return
        self.SelectedDevice = device

        op = self.get_op(device)

        if op != None:
            item = create_menuitem(op, get_icon("network-transmit-recieve", 16))
            item.props.sensitive = False
            item.show()
            self.append(item)
            return

        rets = self.Blueman.Plugins.Run("on_request_menu_items", self, device)

        for ret in rets:
            if ret:
                for (item, pos) in ret:
                    items.append((pos, item))

        if device.Fake:
            item = create_menuitem(_("_Add Device"), get_icon("list-add", 16))
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.add_device(device))
            item.show()
            self.append(item)
            item.props.tooltip_text = _("Add this device to known devices list")

            item = create_menuitem(_("_Setup..."), get_icon("document-properties", 16))
            self.append(item)
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.setup(device))
            item.show()
            item.props.tooltip_text = _("Run the setup assistant for this device")

            item = create_menuitem(_("_Pair"), get_icon("dialog-password", 16))
            self.Signals.Handle("gobject", item, "activate",
                                lambda x: self.Blueman.bond(device))
            self.append(item)
            item.show()
            item.props.tooltip_text = _("Pair with the device")

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            send_item = create_menuitem(_("Send a _File..."), get_icon("edit-copy", 16))
            self.Signals.Handle("gobject", send_item, "activate",
                                lambda x: self.Blueman.send(device))
            send_item.show()
            self.append(send_item)



        else:
            dprint(device.Alias)

            item = None

            have_disconnectables = False
            have_connectables = False

            if True in map(lambda x: x[0] >= 100 and x[0] < 200, items):
                have_disconnectables = True

            if True in map(lambda x: x[0] < 100, items):
                have_connectables = True

            if True in map(lambda x: x[0] >= 200, items) and (have_connectables or have_disconnectables):
                item = Gtk.SeparatorMenuItem()
                item.show()
                items.append((199, item))

            if have_connectables:
                item = Gtk.MenuItem()
                label = Gtk.Label()
                label.set_markup(_("<b>Connect To:</b>"))
                label.props.xalign = 0.0

                label.show()
                item.add(label)
                item.props.sensitive = False
                item.show()
                items.append((0, item))

            if have_disconnectables:
                item = Gtk.MenuItem()
                label = Gtk.Label()
                label.set_markup(_("<b>Disconnect:</b>"))
                label.props.xalign = 0.0

                label.show()
                item.add(label)
                item.props.sensitive = False
                item.show()
                items.append((99, item))

            items.sort(key=itemgetter(0))
            for priority, item in items:
                self.append(item)

            if items != []:
                item = Gtk.SeparatorMenuItem()
                item.show()
                self.append(item)

            del items

            send_item = create_menuitem(_("Send a _File..."), get_icon("edit-copy", 16))
            send_item.props.sensitive = False
            self.append(send_item)
            send_item.show()

            browse_item = create_menuitem(_("_Browse Device..."), get_icon("document-open", 16))
            browse_item.props.sensitive = False
            self.append(browse_item)
            browse_item.show()

            uuids = device.UUIDs
            for uuid in uuids:
                uuid16 = uuid128_to_uuid16(uuid)
                if uuid16 == OBEX_OBJPUSH_SVCLASS_ID:
                    self.Signals.Handle("gobject", send_item, "activate", lambda x: self.Blueman.send(device))
                    send_item.props.sensitive = True

                if uuid16 == OBEX_FILETRANS_SVCLASS_ID:
                    self.Signals.Handle("gobject", browse_item, "activate", lambda x: self.Blueman.browse(device))
                    browse_item.props.sensitive = True

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Pair"), get_icon("dialog-password", 16))
            item.props.tooltip_text = _("Create pairing with the device")
            self.append(item)
            item.show()
            if not device.Paired:
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.bond(device))
            else:
                item.props.sensitive = False

            if not device.Trusted:
                item = create_menuitem(_("_Trust"), get_icon("blueman-trust", 16))
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
                self.append(item)
                item.show()
            else:
                item = create_menuitem(_("_Untrust"), get_icon("blueman-untrust", 16))
                self.append(item)
                self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
                item.show()
            item.props.tooltip_text = _("Mark/Unmark this device as trusted")

            item = create_menuitem(_("_Setup..."), get_icon("document-properties", 16))
            self.append(item)
            self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.setup(device))
            item.show()
            item.props.tooltip_text = _("Run the setup assistant for this device")

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Remove..."), get_icon("edit-delete", 16))
            self.Signals.Handle(item, "activate", lambda x: self.Blueman.remove(device))
            self.append(item)
            item.show()
            item.props.tooltip_text = _("Remove this device from the known devices list")

            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            item = create_menuitem(_("_Disconnect"), get_icon("network-offline", 16))
            item.props.tooltip_text = _("Forcefully disconnect the device")

            self.append(item)
            item.show()

            def on_disconnect(item):
                def finished(*args):
                    self.unset_op(device)

                self.set_op(device, _("Disconnecting..."))
                self.Blueman.disconnect(device,
                                        reply_handler=finished,
                                        error_handler=finished)

            if device.Connected:
                self.Signals.Handle(item, "activate", on_disconnect)

            else:
                item.props.sensitive = False