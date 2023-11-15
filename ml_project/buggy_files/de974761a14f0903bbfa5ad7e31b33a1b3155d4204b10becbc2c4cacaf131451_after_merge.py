    def set_adapter(self, adapter=None):
        self.clear()
        if self.discovering:
            self.stop_discovery()
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))

        adapter = adapter_path_to_name(adapter)

        logging.debug("Setting adapter to: %s " % adapter)

        if adapter is not None:
            try:
                self.Adapter = self.manager.get_adapter(adapter)
                self.__adapter_path = self.Adapter.get_object_path()
                self.emit("adapter-changed", self.__adapter_path)
            except bluez.errors.DBusNoSuchAdapterError:
                logging.warning('Failed to set adapter, trying first available.')
                self.set_adapter(None)
                return
        else:
            adapters = self.manager.get_adapters()
            if len(adapters) > 0:
                self.Adapter = adapters[0]
                self.__adapter_path = self.Adapter.get_object_path()
            else:
                self.Adapter = None
                self.__adapter_path = None

        self.emit("adapter-changed", self.__adapter_path)