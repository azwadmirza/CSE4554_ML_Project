    def generate_adapter_menu(self):
        menu = Gtk.Menu()

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        settings = Gtk.ImageMenuItem.new_from_stock("gtk-preferences", None)
        settings.connect("activate", lambda x: self.blueman.adapter_properties())
        settings.show()
        menu.append(settings)

        group = []
        for adapter in self.adapters:
            props = adapter.get_properties()
            item = Gtk.RadioMenuItem.new_with_label(group, props["Name"])
            group = item.get_group()

            item.connect("activate", self.on_adapter_selected, adapter.get_object_path())
            if adapter.get_object_path() == self.blueman.List.Adapter.get_object_path():
                item.props.active = True

            item.show()
            menu.prepend(item)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.prepend(sep)

        item = create_menuitem(_("_Search"), get_icon("gtk-find", 16))
        item.connect("activate", lambda x: self.blueman.inquiry())
        item.show()
        menu.prepend(item)
        self.Search = item

        m = self.item_adapter.get_submenu()
        if m != None:
            m.deactivate()
        self.item_adapter.set_submenu(menu)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        item = Gtk.ImageMenuItem.new_from_stock("gtk-quit", None)
        item.connect("activate", lambda x: Gtk.main_quit())
        item.show()
        menu.append(item)