    def __init__(self, interface, obj_path):
        super(PropertiesBase, self).__init__(interface, obj_path)

        self._handler_wrappers = {}

        if obj_path:
            self.__properties_interface = dbus.Interface(self._dbus_proxy, 'org.freedesktop.DBus.Properties')

        self._handle_signal(self._on_properties_changed, 'PropertiesChanged', 'org.freedesktop.DBus.Properties',
                            path_keyword='path')