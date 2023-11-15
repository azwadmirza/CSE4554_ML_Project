    def detach(self, session):
        """
        Implements :func:`crossbar.router.interfaces.IDealer.detach`
        """
        if session in self._session_to_registrations:
            # send out Errors for any in-flight calls we have
            outstanding = self._callee_to_invocations.get(session, [])
            for invoke in outstanding:
                self.log.debug(
                    "Cancelling in-flight INVOKE with id={request} on"
                    " session {session}",
                    request=invoke.call.request,
                    session=session._session_id,
                )
                reply = message.Error(
                    message.Call.MESSAGE_TYPE,
                    invoke.call.request,
                    ApplicationError.CANCELED,
                    [u"callee disconnected from in-flight request"],
                )
                # send this directly to the caller's session
                invoke.caller._transport.send(reply)

            for registration in self._session_to_registrations[session]:
                was_registered, was_last_callee = self._registration_map.drop_observer(session, registration)

                if was_registered and was_last_callee:
                    self._registration_map.delete_observation(registration)

                # publish WAMP meta events
                #
                if self._router._realm:
                    service_session = self._router._realm.session
                    if service_session and not registration.uri.startswith(u'wamp.'):
                        if was_registered:
                            service_session.publish(u'wamp.registration.on_unregister', session._session_id, registration.id)
                        if was_last_callee:
                            service_session.publish(u'wamp.registration.on_delete', session._session_id, registration.id)

            del self._session_to_registrations[session]

        else:
            raise Exception(u"session with ID {} not attached".format(session._session_id))