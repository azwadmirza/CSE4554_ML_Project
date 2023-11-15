def create_native_worker_client_factory(router_session_factory, on_ready, on_exit):
    """
    Create a transport factory for talking to native workers.

    The node controller talks WAMP-WebSocket-over-STDIO with spawned (native) workers.

    The node controller runs a client transport factory, and the native worker
    runs a server transport factory. This is a little non-intuitive, but just the
    way that Twisted works when using STDIO transports.

    :param router_session_factory: Router session factory to attach to.
    :type router_session_factory: obj
    """
    factory = NativeWorkerClientFactory(router_session_factory, "ws://localhost", debug=False)

    # we need to increase the opening handshake timeout in particular, since starting up a worker
    # on PyPy will take a little (due to JITting)
    factory.setProtocolOptions(failByDrop=False, openHandshakeTimeout=60, closeHandshakeTimeout=5)

    # on_ready is resolved in crossbar/controller/process.py:on_worker_ready around 175
    # after crossbar.node.<ID>.on_worker_ready is published to (in the controller session)
    # that happens in crossbar/worker/worker.py:publish_ready which itself happens when
    # the native worker joins the realm (part of onJoin)
    factory._on_ready = on_ready
    factory._on_exit = on_exit

    return factory