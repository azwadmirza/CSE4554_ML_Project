    def stop_component(self, component_id, details=None):
        """
        Stop a component currently running within this container.

        :param component_id: The ID of the component to stop.
        :type component_id: int

        :param details: Caller details.
        :type details: instance of :class:`autobahn.wamp.types.CallDetails`

        :returns: Stop information.
        :rtype: dict
        """
        self.log.debug('{klass}.stop_component({component_id}, {details})', klass=self.__class__.__name__, component_id=component_id, details=details)

        if component_id not in self.components:
            raise ApplicationError(u'crossbar.error.no_such_object', 'no component with ID {} running in this container'.format(component_id))

        component = self.components[component_id]

        try:
            component.proto.close()
        except:
            self.log.failure("failed to close protocol on component '{component_id}': {log_failure}", component_id=component_id)
            raise
        else:
            # essentially just waiting for "on_component_stop"
            yield component._stopped

        stopped = {
            u'component_id': component_id,
            u'uptime': (datetime.utcnow() - component.started).total_seconds(),
            u'caller': {
                u'session': details.caller if details else None,
                u'authid': details.caller_authid if details else None,
                u'authrole': details.caller_authrole if details else None,
            }
        }

        # the component.proto above normally already cleaned it up
        if component_id in self.components:
            del self.components[component_id]

        # FIXME: this is getting autobahn.wamp.exception.TransportLost
        if False:
            self.publish(u'{}.on_component_stopped'.format(self._uri_prefix),
                         stopped,
                         options=PublishOptions(exclude=details.caller))

        returnValue(stopped)