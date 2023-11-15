    def processCall(self, session, call):
        """
        Implements :func:`crossbar.router.interfaces.IDealer.processCall`
        """
        if self._router.is_traced:
            if not call.correlation_id:
                call.correlation_id = self._router.new_correlation_id()
                call.correlation_is_anchor = True
                call.correlation_is_last = False
            if not call.correlation_uri:
                call.correlation_uri = call.procedure
            self._router._factory._worker._maybe_trace_rx_msg(session, call)

        # check procedure URI: for CALL, must be valid URI (either strict or loose), and
        # all URI components must be non-empty
        if self._option_uri_strict:
            uri_is_valid = _URI_PAT_STRICT_NON_EMPTY.match(call.procedure)
        else:
            uri_is_valid = _URI_PAT_LOOSE_NON_EMPTY.match(call.procedure)

        if not uri_is_valid:
            reply = message.Error(message.Call.MESSAGE_TYPE, call.request, ApplicationError.INVALID_URI, [u"call with invalid procedure URI '{0}' (URI strict checking {1})".format(call.procedure, self._option_uri_strict)])
            reply.correlation_id = call.correlation_id
            reply.correlation_uri = call.procedure
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)
            return

        # authorize CALL action
        #
        d = self._router.authorize(session, call.procedure, u'call', options=call.marshal_options())

        def on_authorize_success(authorization):
            # the call to authorize the action _itself_ succeeded. now go on depending on whether
            # the action was actually authorized or not ..
            #
            if not authorization[u'allow']:
                reply = message.Error(
                    message.Call.MESSAGE_TYPE,
                    call.request,
                    ApplicationError.NOT_AUTHORIZED,
                    [u"session is not authorized to call procedure '{0}'".format(call.procedure)]
                )
                reply.correlation_id = call.correlation_id
                reply.correlation_uri = call.procedure
                reply.correlation_is_anchor = False
                reply.correlation_is_last = True
                self._router.send(session, reply)

            else:
                # get registrations active on the procedure called
                #
                registration = self._registration_map.best_matching_observation(call.procedure)

                if registration:

                    # validate payload (skip in "payload_transparency" mode)
                    #
                    if call.payload is None:
                        try:
                            self._router.validate(u'call', call.procedure, call.args, call.kwargs)
                        except Exception as e:
                            reply = message.Error(message.Call.MESSAGE_TYPE, call.request, ApplicationError.INVALID_ARGUMENT, [u"call of procedure '{0}' with invalid application payload: {1}".format(call.procedure, e)])
                            reply.correlation_id = call.correlation_id
                            reply.correlation_uri = call.procedure
                            reply.correlation_is_anchor = False
                            reply.correlation_is_last = True
                            self._router.send(session, reply)
                            return

                    # now actually perform the invocation of the callee ..
                    #
                    self._call(session, call, registration, authorization)
                else:
                    reply = message.Error(message.Call.MESSAGE_TYPE, call.request, ApplicationError.NO_SUCH_PROCEDURE, [u"no callee registered for procedure <{0}>".format(call.procedure)])
                    reply.correlation_id = call.correlation_id
                    reply.correlation_uri = call.procedure
                    reply.correlation_is_anchor = False
                    reply.correlation_is_last = True
                    self._router.send(session, reply)

        def on_authorize_error(err):
            """
            the call to authorize the action _itself_ failed (note this is
            different from the call to authorize succeed, but the
            authorization being denied)
            """
            self.log.failure("Authorization of 'call' for '{uri}' failed", uri=call.procedure, failure=err)
            reply = message.Error(
                message.Call.MESSAGE_TYPE,
                call.request,
                ApplicationError.AUTHORIZATION_FAILED,
                [u"failed to authorize session for calling procedure '{0}': {1}".format(call.procedure, err.value)]
            )
            reply.correlation_id = call.correlation_id
            reply.correlation_uri = call.procedure
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)

        txaio.add_callbacks(d, on_authorize_success, on_authorize_error)