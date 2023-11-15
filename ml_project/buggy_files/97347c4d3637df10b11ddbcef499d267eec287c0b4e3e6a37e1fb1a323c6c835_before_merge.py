    def get_properties(self):
        prop_names = self._dbus_proxy.get_cached_property_names()
        result = {}
        for name in prop_names:
            result[name] = self._dbus_proxy.get_cached_property(name).unpack()

        if result:
            for k, v in self.__fallback.items():
                if k in result: continue
                else: result[k] = v

            return result