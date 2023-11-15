    def on_item_activated(self, item):
        logging.info("Connect %s %s" % (item["address"], item["uuid"]))

        item["mitem"]["sensitive"] = False
        self.parent.Plugins.Menu.on_menu_changed()

        def reply(*args):
            Notification(_("Connected"), _("Connected to %s") % item["mitem"]["text"],
                         icon_name=item["icon"]).show()
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        def err(reason):
            Notification(_("Failed to connect"), str(reason).split(": ")[-1],
                         icon_name="dialog-error").show()
            item["mitem"]["sensitive"] = True
            self.parent.Plugins.Menu.on_menu_changed()

        self.parent.Plugins.DBusService.connect_service(item["device"], item["uuid"], reply, err)