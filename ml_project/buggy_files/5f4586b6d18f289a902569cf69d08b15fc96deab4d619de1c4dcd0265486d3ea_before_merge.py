    def get(self, name):
        prop = self._dbus_proxy.get_cached_property(name)

        if prop is not None:
            return prop.unpack()
        elif not prop and name in self.__fallback:
            return self.__fallback[name]
        else:
            raise BluezDBusException("No such property '%s'" % name)