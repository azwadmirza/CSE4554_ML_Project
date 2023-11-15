    def _wrap_connection_future(self, transport, done, conn_f):

        def on_connect_success(result):
            # async connect call returns a 2-tuple
            transport, proto = result

            # in the case where we .abort() the transport / connection
            # during setup, we still get on_connect_success but our
            # transport is already closed (this will happen if
            # e.g. there's an "open handshake timeout") -- I don't
            # know if there's a "better" way to detect this? #python
            # doesn't know of one, anyway
            if transport.is_closing():
                if not txaio.is_called(done):
                    reason = getattr(proto, "_onclose_reason", "Connection already closed")
                    txaio.reject(done, TransportLost(reason))
                return

            # if e.g. an SSL handshake fails, we will have
            # successfully connected (i.e. get here) but need to
            # 'listen' for the "connection_lost" from the underlying
            # protocol in case of handshake failure .. so we wrap
            # it. Also, we don't increment transport.success_count
            # here on purpose (because we might not succeed).

            # XXX double-check that asyncio behavior on TLS handshake
            # failures is in fact as described above
            orig = proto.connection_lost

            @wraps(orig)
            def lost(fail):
                rtn = orig(fail)
                if not txaio.is_called(done):
                    # asyncio will call connection_lost(None) in case of
                    # a transport failure, in which case we create an
                    # appropriate exception
                    if fail is None:
                        fail = TransportLost("failed to complete connection")
                    txaio.reject(done, fail)
                return rtn
            proto.connection_lost = lost

        def on_connect_failure(err):
            transport.connect_failures += 1
            # failed to establish a connection in the first place
            txaio.reject(done, err)

        txaio.add_callbacks(conn_f, on_connect_success, None)
        # the errback is added as a second step so it gets called if
        # there as an error in on_connect_success itself.
        txaio.add_callbacks(conn_f, None, on_connect_failure)
        return conn_f