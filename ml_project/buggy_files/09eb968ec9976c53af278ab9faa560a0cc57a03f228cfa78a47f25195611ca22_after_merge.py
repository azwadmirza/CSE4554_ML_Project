    def onMessage(self, msg):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onMessage`
        """
        if self._session_id is None:

            if not self._pending_session_id:
                self._pending_session_id = util.id()

            def welcome(realm, authid=None, authrole=None, authmethod=None, authprovider=None, authextra=None, custom=None):
                self._realm = realm
                self._session_id = self._pending_session_id
                self._pending_session_id = None
                self._goodbye_sent = False

                self._router = self._router_factory.get(realm)
                if not self._router:
                    # should not arrive here
                    raise Exception("logic error (no realm at a stage were we should have one)")

                self._authid = authid
                self._authrole = authrole
                self._authmethod = authmethod
                self._authprovider = authprovider
                self._authextra = authextra or {}

                self._authextra[u'x_cb_node_id'] = self._router_factory._node_id
                self._authextra[u'x_cb_peer'] = str(self._transport.peer)
                self._authextra[u'x_cb_pid'] = os.getpid()

                roles = self._router.attach(self)

                msg = message.Welcome(self._session_id,
                                      roles,
                                      realm=realm,
                                      authid=authid,
                                      authrole=authrole,
                                      authmethod=authmethod,
                                      authprovider=authprovider,
                                      authextra=self._authextra,
                                      custom=custom)
                self._transport.send(msg)

                self.onJoin(SessionDetails(self._realm, self._session_id, self._authid, self._authrole, self._authmethod, self._authprovider, self._authextra))

            # the first message MUST be HELLO
            if isinstance(msg, message.Hello):

                self._session_roles = msg.roles

                details = types.HelloDetails(realm=msg.realm,
                                             authmethods=msg.authmethods,
                                             authid=msg.authid,
                                             authrole=msg.authrole,
                                             authextra=msg.authextra,
                                             session_roles=msg.roles,
                                             pending_session=self._pending_session_id)

                d = txaio.as_future(self.onHello, msg.realm, details)

                def success(res):
                    msg = None
                    # it is possible this session has disconnected
                    # while onHello was taking place
                    if self._transport is None:
                        self.log.info(
                            "Client session disconnected during authentication",
                        )
                        return

                    if isinstance(res, types.Accept):
                        custom = {
                            u'x_cb_node_id': self._router_factory._node_id
                        }
                        welcome(res.realm, res.authid, res.authrole, res.authmethod, res.authprovider, res.authextra, custom)

                    elif isinstance(res, types.Challenge):
                        msg = message.Challenge(res.method, res.extra)

                    elif isinstance(res, types.Deny):
                        msg = message.Abort(res.reason, res.message)

                    else:
                        pass

                    if msg:
                        self._transport.send(msg)

                txaio.add_callbacks(d, success, self._swallow_error_and_abort)

            elif isinstance(msg, message.Authenticate):

                d = txaio.as_future(self.onAuthenticate, msg.signature, {})

                def success(res):
                    msg = None
                    # it is possible this session has disconnected
                    # while authentication was taking place
                    if self._transport is None:
                        self.log.info(
                            "Client session disconnected during authentication",
                        )
                        return

                    if isinstance(res, types.Accept):
                        custom = {
                            u'x_cb_node_id': self._router_factory._node_id
                        }
                        welcome(res.realm, res.authid, res.authrole, res.authmethod, res.authprovider, res.authextra, custom)

                    elif isinstance(res, types.Deny):
                        msg = message.Abort(res.reason, res.message)

                    else:
                        pass

                    if msg:
                        self._transport.send(msg)

                txaio.add_callbacks(d, success, self._swallow_error_and_abort)

            elif isinstance(msg, message.Abort):

                # fire callback and close the transport
                self.onLeave(types.CloseDetails(msg.reason, msg.message))

                self._session_id = None
                self._pending_session_id = None

                # self._transport.close()

            else:
                # raise ProtocolError(u"PReceived {0} message while session is not joined".format(msg.__class__))
                # self.log.warn('Protocol state error - received {message} while session is not joined')
                # swallow all noise like still getting PUBLISH messages from log event forwarding - maybe FIXME
                pass

        else:

            if isinstance(msg, message.Hello):
                raise ProtocolError(u"HELLO message received, while session is already established")

            elif isinstance(msg, message.Goodbye):
                if not self._goodbye_sent:
                    # The peer wants to close: answer with GOODBYE reply.
                    # Note: We MUST NOT send any WAMP message _after_ GOODBYE
                    reply = message.Goodbye()
                    self._transport.send(reply)
                    self._goodbye_sent = True
                else:
                    # This is the peer's GOODBYE reply to our own earlier GOODBYE
                    pass

                # We need to first detach the session from the router before
                # erasing the session ID below ..
                try:
                    self._router.detach(self)
                except Exception:
                    self.log.failure("Internal error")

                # In order to send wamp.session.on_leave properly
                # (i.e. *with* the proper session_id) we save it
                previous_session_id = self._session_id

                # At this point, we've either sent GOODBYE already earlier,
                # or we have just responded with GOODBYE. In any case, we MUST NOT
                # send any WAMP message from now on:
                # clear out session ID, so that anything that might be triggered
                # in the onLeave below is prohibited from sending WAMP stuff.
                # E.g. the client might have been subscribed to meta events like
                # wamp.session.on_leave - and we must not send that client's own
                # leave to itself!
                self._session_id = None
                self._pending_session_id = None

                # publish event, *after* self._session_id is None so
                # that we don't publish to ourselves as well (if this
                # session happens to be subscribed to wamp.session.on_leave)
                if self._service_session:
                    self._service_session.publish(
                        u'wamp.session.on_leave',
                        previous_session_id,
                    )

                # fire callback and close the transport
                self.onLeave(types.CloseDetails(msg.reason, msg.message))

                # don't close the transport, as WAMP allows to reattach a session
                # to the same or a different realm without closing the transport
                # self._transport.close()

            else:
                self._router.process(self, msg)