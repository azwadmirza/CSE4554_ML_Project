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