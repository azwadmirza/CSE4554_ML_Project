    def connected(self):
        try:
            return self._service.get_properties()['Connected']
        except DBusException as e:
            dprint('Could not get properties of network service: %s' % e)
            return False