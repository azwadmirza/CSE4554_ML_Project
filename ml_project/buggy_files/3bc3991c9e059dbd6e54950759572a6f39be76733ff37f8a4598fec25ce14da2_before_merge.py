    def authorize(self, session, uri, action, options):
        """
        Authorize a session connected under this role to perform the given
        action on the given URI.

        :param session: The WAMP session that requests the action.
        :type session: Instance of :class:`autobahn.wamp.protocol.ApplicationSession`
        :param uri: The URI on which to perform the action.
        :type uri: str
        :param action: The action to be performed.
        :type action: str

        :return: bool -- Flag indicating whether session is authorized or not.
        """
        session_details = getattr(session, '_session_details', None)
        if session_details is None:
            # this happens for "embedded" sessions -- perhaps we
            # should have a better way to detect this -- also
            # session._transport should be a RouterApplicationSession
            session_details = {
                u'session': session._session_id,
                u'authid': session._authid,
                u'authrole': session._authrole,
                u'authmethod': session._authmethod,
                u'authprovider': session._authprovider,
                u'authextra': session._authextra,
                u'transport': {
                    u'type': u'stdio',  # or maybe "embedded"?
                }
            }

        self.log.debug(
            "CrossbarRouterRoleDynamicAuth.authorize {uri} {action} {details}",
            uri=uri, action=action, details=session_details)

        d = self._session.call(self._authorizer, session_details, uri, action, options)

        # we could do backwards-compatibility for clients that didn't
        # yet add the 5th "options" argument to their authorizers like
        # so:
        def maybe_call_old_way(result):
            if isinstance(result, Failure):
                if isinstance(result.value, ApplicationError):
                    if 'takes exactly 4 arguments' in str(result.value):
                        self.log.warn(
                            "legacy authorizer '{auth}'; should take 5 arguments. Calling with 4.",
                            auth=self._authorizer,
                        )
                        return self._session.call(self._authorizer, session_details, uri, action)
            return result
        d.addBoth(maybe_call_old_way)

        def sanity_check(authorization):
            """
            Ensure the return-value we got from the user-supplied method makes sense
            """
            if isinstance(authorization, dict):
                for key in authorization.keys():
                    if key not in [u'allow', u'cache', u'disclose']:
                        return Failure(
                            ValueError(
                                "Authorizer returned unknown key '{key}'".format(
                                    key=key,
                                )
                            )
                        )
                # must have "allow"
                if u'allow' not in authorization:
                    return Failure(
                        ValueError(
                            "Authorizer must have 'allow' in returned dict"
                        )
                    )
                # all values must be bools
                for key, value in authorization.items():
                    if not isinstance(value, bool):
                        return Failure(
                            ValueError(
                                "Authorizer must have bool for '{}'".format(key)
                            )
                        )
                return authorization

            elif isinstance(authorization, bool):
                return authorization

            return Failure(
                ValueError(
                    "Authorizer returned unknown type '{name}'".format(
                        name=type(authorization).__name__,
                    )
                )
            )
        d.addCallback(sanity_check)
        return d