    def publish(self):
        if not dbus:
            logger.debug('Zeroconf publish failed: dbus not installed.')
            return False

        try:
            bus = dbus.SystemBus()
        except dbus.exceptions.DBusException as e:
            logger.debug('Zeroconf publish failed: %s', e)
            return False

        if not bus.name_has_owner('org.freedesktop.Avahi'):
            logger.debug('Zeroconf publish failed: Avahi service not running.')
            return False

        server = dbus.Interface(bus.get_object('org.freedesktop.Avahi', '/'),
                                'org.freedesktop.Avahi.Server')

        self.group = dbus.Interface(
            bus.get_object('org.freedesktop.Avahi', server.EntryGroupNew()),
            'org.freedesktop.Avahi.EntryGroup')

        text = [_convert_text_to_dbus_bytes(t) for t in self.text]
        self.group.AddService(_AVAHI_IF_UNSPEC, _AVAHI_PROTO_UNSPEC,
                              dbus.UInt32(_AVAHI_PUBLISHFLAGS_NONE),
                              self.name, self.stype, self.domain, self.host,
                              dbus.UInt16(self.port), text)

        self.group.Commit()
        return True