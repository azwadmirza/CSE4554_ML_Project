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

                # if the session disconencted while the authorization
                # was being checked, 'registration' will be None and
                # we'll (correctly) fire an error.

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