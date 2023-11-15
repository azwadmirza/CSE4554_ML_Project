    def __init__(self, parent, plugin_name, count):
        title = ngettext("Run the plugin \"%(name)s\" on %(count)d album?",
                         "Run the plugin \"%(name)s\" on %(count)d albums?",
                         count) % {'name':plugin_name, 'count': count}

        super(ConfirmMultiAlbumInvoke, self).__init__(
            get_top_parent(parent),
            title, "",
            buttons=Gtk.ButtonsType.NONE)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        delete_button = Button(_("_Run Plugin"), Gtk.STOCK_EXECUTE)
        delete_button.show()
        self.add_action_widget(delete_button, self.RESPONSE_INVOKE)
        self.set_default_response(Gtk.ResponseType.CANCEL)