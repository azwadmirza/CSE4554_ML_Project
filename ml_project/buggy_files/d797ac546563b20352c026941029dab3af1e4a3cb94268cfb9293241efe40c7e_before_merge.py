    def __init__(self, instance):
        GObject.GObject.__init__(self)

        self.Properties = {}
        self.Temp = False

        if hasattr(instance, "format") and hasattr(instance, "upper"):
            self.Device = BluezDevice(instance)
        else:
            self.Device = instance

        #set fallback icon, fixes lp:#327718
        self.Device.Icon = "blueman"
        self.Device.Class = "unknown"

        self.Valid = True

        dprint("caching initial properties")
        self.Properties = self.Device.get_properties()

        w = weakref.ref(self)
        self._obj_path = self.Device.get_object_path()
        self.Device.connect_signal('property-changed',
                                   lambda _device, key, value: w() and w().property_changed(key, value))
        self._manager = Manager()
        self._manager.connect_signal('device-removed', lambda _adapter, path: w() and w().on_device_removed(path))