    def get_properties(self):
        param = GLib.Variant('(s)', (self._interface_name,))
        res = self._call('GetAll', param, True)
        prop_names = res[0].keys()

        result = {}
        for name in prop_names:
            result[name] = self.get(name)

        if result:
            for k, v in self.__fallback.items():
                if k in result: continue
                else: result[k] = v

            return result