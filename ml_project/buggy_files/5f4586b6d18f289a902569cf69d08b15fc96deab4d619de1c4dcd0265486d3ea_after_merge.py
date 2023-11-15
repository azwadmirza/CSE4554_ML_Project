    def get(self, name):
        prop = self._dbus_proxy.get_cached_property(name)

        if prop is None and name in self.__fallback:
            return self.__fallback[name]
        elif prop is None:
            # Fallback when cached property is not available
            param = GLib.Variant('(ss)', (self._interface_name, name))
            try:
                prop = self._call('Get', param, True)
                return prop[0]
            except GLib.GError:
                raise BluezDBusException("No such property '%s'" % name)
        elif prop is not None:
            return prop.unpack()
        else:
            raise BluezDBusException("No such property '%s'" % name)