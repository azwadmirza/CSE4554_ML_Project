        def on_connect_success(result):
            # async connect call returns a 2-tuple
            transport, proto = result

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