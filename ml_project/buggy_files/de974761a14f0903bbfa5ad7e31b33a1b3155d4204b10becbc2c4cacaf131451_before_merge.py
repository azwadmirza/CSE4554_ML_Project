    def set_adapter(self, adapter=None):
        self.clear()
        if self.discovering:
            self.stop_discovery()
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))

        adapter = adapter_path_to_name(adapter)

        logging.debug(adapter)

        # The pattern may be incorrect (ie removed adapter), see #590
        try:
            self.Adapter = self.manager.get_adapter(adapter)
        except bluez.errors.DBusNoSuchAdapterError:
            logging.info('Adapter pattern not valid, trying default adapter.')

        try:
            self.Adapter = self.manager.get_adapter()
            self.__adapter_path = self.Adapter.get_object_path()
        except bluez.errors.DBusNoSuchAdapterError as e:
            logging.exception(e)
            self.Adapter = None
            self.__adapter_path = None
        finally:
            self.emit("adapter-changed", None)