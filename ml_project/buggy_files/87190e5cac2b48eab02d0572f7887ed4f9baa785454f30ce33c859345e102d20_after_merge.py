    def processRegister(self, session, register):
        """
        Implements :func:`crossbar.router.interfaces.IDealer.processRegister`
        """
        # check topic URI: for SUBSCRIBE, must be valid URI (either strict or loose), and all
        # URI components must be non-empty other than for wildcard subscriptions
        #
        if self._router.is_traced:
            if not register.correlation_id:
                register.correlation_id = self._router.new_correlation_id()
                register.correlation_is_anchor = True
                register.correlation_is_last = False
            if not register.correlation_uri:
                register.correlation_uri = register.procedure
            self._router._factory._worker._maybe_trace_rx_msg(session, register)

        if self._option_uri_strict:
            if register.match == u"wildcard":
                uri_is_valid = _URI_PAT_STRICT_EMPTY.match(register.procedure)
            elif register.match == u"prefix":
                uri_is_valid = _URI_PAT_STRICT_LAST_EMPTY.match(register.procedure)
            elif register.match == u"exact":
                uri_is_valid = _URI_PAT_STRICT_NON_EMPTY.match(register.procedure)
            else:
                # should not arrive here
                raise Exception("logic error")
        else:
            if register.match == u"wildcard":
                uri_is_valid = _URI_PAT_LOOSE_EMPTY.match(register.procedure)
            elif register.match == u"prefix":
                uri_is_valid = _URI_PAT_LOOSE_LAST_EMPTY.match(register.procedure)
            elif register.match == u"exact":
                uri_is_valid = _URI_PAT_LOOSE_NON_EMPTY.match(register.procedure)
            else:
                # should not arrive here
                raise Exception("logic error")

        if not uri_is_valid:
            reply = message.Error(message.Register.MESSAGE_TYPE, register.request, ApplicationError.INVALID_URI, [u"register for invalid procedure URI '{0}' (URI strict checking {1})".format(register.procedure, self._option_uri_strict)])
            reply.correlation_id = register.correlation_id
            reply.correlation_uri = register.procedure
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)
            return

        # disallow registration of procedures starting with "wamp." other than for
        # trusted sessions (that are sessions built into Crossbar.io routing core)
        #
        if session._authrole is not None and session._authrole != u"trusted":
            is_restricted = register.procedure.startswith(u"wamp.")
            if is_restricted:
                reply = message.Error(message.Register.MESSAGE_TYPE, register.request, ApplicationError.INVALID_URI, [u"register for restricted procedure URI '{0}')".format(register.procedure)])
                reply.correlation_id = register.correlation_id
                reply.correlation_uri = register.procedure
                reply.correlation_is_anchor = False
                reply.correlation_is_last = True
                self._router.send(session, reply)
                return

        # authorize REGISTER action
        #
        d = self._router.authorize(session, register.procedure, u'register', options=register.marshal_options())

        def on_authorize_success(authorization):
            # check the authorization before ANYTHING else, otherwise
            # we may leak information about already-registered URIs
            # etc.
            if not authorization[u'allow']:
                # error reply since session is not authorized to register
                #
                reply = message.Error(
                    message.Register.MESSAGE_TYPE,
                    register.request,
                    ApplicationError.NOT_AUTHORIZED,
                    [u"session is not authorized to register procedure '{0}'".format(register.procedure)],
                )

            # get existing registration for procedure / matching strategy - if any
            #
            registration = self._registration_map.get_observation(register.procedure, register.match)

            # if the session disconencted while the authorization was
            # being checked, stop
            if session not in self._session_to_registrations:
                # if the session *really* disconnected, it won't have
                # a _session_id any longer, so we double-check
                if session._session_id is not None:
                    self.log.error(
                        "Session '{session_id}' still appears valid, but isn't in registration map",
                        session_id=session._session_id,
                    )
                self.log.info(
                    "Session vanished while registering '{procedure}'",
                    procedure=register.procedure,
                )
                assert registration is None
                return

            # if force_reregister was enabled, we only do any actual
            # kicking of existing registrations *after* authorization
            if registration and not register.force_reregister:
                # there is an existing registration, and that has an
                # invocation strategy that only allows a single callee
                # on a the given registration
                #
                if registration.extra.invoke == message.Register.INVOKE_SINGLE:
                    reply = message.Error(
                        message.Register.MESSAGE_TYPE,
                        register.request,
                        ApplicationError.PROCEDURE_ALREADY_EXISTS,
                        [u"register for already registered procedure '{0}'".format(register.procedure)]
                    )
                    reply.correlation_id = register.correlation_id
                    reply.correlation_uri = register.procedure
                    reply.correlation_is_anchor = False
                    reply.correlation_is_last = True
                    self._router.send(session, reply)
                    return

                # there is an existing registration, and that has an
                # invokation strategy different from the one requested
                # by the new callee
                #
                if registration.extra.invoke != register.invoke:
                    reply = message.Error(
                        message.Register.MESSAGE_TYPE,
                        register.request,
                        ApplicationError.PROCEDURE_EXISTS_INVOCATION_POLICY_CONFLICT,
                        [
                            u"register for already registered procedure '{0}' "
                            u"with conflicting invocation policy (has {1} and "
                            u"{2} was requested)".format(
                                register.procedure,
                                registration.extra.invoke,
                                register.invoke
                            )
                        ]
                    )
                    reply.correlation_id = register.correlation_id
                    reply.correlation_uri = register.procedure
                    reply.correlation_is_anchor = False
                    reply.correlation_is_last = True
                    self._router.send(session, reply)
                    return

            # this check is a little redundant, because theoretically
            # we already returned (above) if this was False, but for safety...
            if authorization[u'allow']:
                registration = self._registration_map.get_observation(register.procedure, register.match)
                if register.force_reregister and registration:
                    for obs in registration.observers:
                        self._registration_map.drop_observer(obs, registration)
                        kicked = message.Unregistered(
                            0,
                            registration=registration.id,
                            reason=u"wamp.error.unregistered",
                        )
                        kicked.correlation_id = register.correlation_id
                        kicked.correlation_uri = register.procedure
                        kicked.correlation_is_anchor = False
                        kicked.correlation_is_last = False
                        self._router.send(obs, kicked)
                    self._registration_map.delete_observation(registration)

                # ok, session authorized to register. now get the registration
                #
                registration_extra = RegistrationExtra(register.invoke)
                registration_callee_extra = RegistrationCalleeExtra(register.concurrency)
                registration, was_already_registered, is_first_callee = self._registration_map.add_observer(session, register.procedure, register.match, registration_extra, registration_callee_extra)

                if not was_already_registered:
                    self._session_to_registrations[session].add(registration)

                # acknowledge register with registration ID
                #
                reply = message.Registered(register.request, registration.id)
                reply.correlation_id = register.correlation_id
                reply.correlation_uri = register.procedure
                reply.correlation_is_anchor = False

                # publish WAMP meta events, if we have a service session, but
                # not for the meta API itself!
                #
                if self._router._realm and \
                   self._router._realm.session and \
                   not registration.uri.startswith(u'wamp.') and \
                   (is_first_callee or not was_already_registered):

                    reply.correlation_is_last = False

                    # when this message was forwarded from other nodes, exclude all such nodes
                    # from receiving the meta event we'll publish below by authid (of the r2r link
                    # from the forwarding node connected to this router node)
                    exclude_authid = None
                    if register.forward_for:
                        exclude_authid = [ff['authid'] for ff in register.forward_for]
                        self.log.info('WAMP meta event will be published excluding these authids (from forward_for): {exclude_authid}',
                                      exclude_authid=exclude_authid)

                    def _publish():
                        service_session = self._router._realm.session

                        if exclude_authid or self._router.is_traced:
                            options = types.PublishOptions(
                                correlation_id=register.correlation_id,
                                correlation_is_anchor=False,
                                correlation_is_last=False,
                                exclude_authid=exclude_authid,
                            )
                        else:
                            options = None

                        if is_first_callee:
                            registration_details = {
                                u'id': registration.id,
                                u'created': registration.created,
                                u'uri': registration.uri,
                                u'match': registration.match,
                                u'invoke': registration.extra.invoke,
                            }
                            service_session.publish(
                                u'wamp.registration.on_create',
                                session._session_id,
                                registration_details,
                                options=options
                            )

                        if not was_already_registered:
                            if options:
                                options.correlation_is_last = True

                            service_session.publish(
                                u'wamp.registration.on_register',
                                session._session_id,
                                registration.id,
                                options=options
                            )
                    # we postpone actual sending of meta events until we return to this client session
                    self._reactor.callLater(0, _publish)

                else:
                    reply.correlation_is_last = True

            # send out reply to register requestor
            #
            self._router.send(session, reply)

        def on_authorize_error(err):
            """
            the call to authorize the action _itself_ failed (note this is
            different from the call to authorize succeed, but the
            authorization being denied)
            """
            self.log.failure("Authorization of 'register' for '{uri}' failed",
                             uri=register.procedure, failure=err)
            reply = message.Error(
                message.Register.MESSAGE_TYPE,
                register.request,
                ApplicationError.AUTHORIZATION_FAILED,
                [u"failed to authorize session for registering procedure '{0}': {1}".format(register.procedure, err.value)]
            )
            reply.correlation_id = register.correlation_id
            reply.correlation_uri = register.procedure
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)

        txaio.add_callbacks(d, on_authorize_success, on_authorize_error)