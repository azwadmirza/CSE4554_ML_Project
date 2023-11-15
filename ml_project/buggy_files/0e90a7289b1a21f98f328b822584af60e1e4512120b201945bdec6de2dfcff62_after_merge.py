  def __init__(self, server_address, runner_factory, context_lock,
               handler_class=None, bind_and_activate=True):
    """Override of TCPServer.__init__().

    N.B. the majority of this function is copied verbatim from TCPServer.__init__().

    :param tuple server_address: An address tuple of (hostname, port) for socket.bind().
    :param class runner_factory: A factory function for creating a DaemonPantsRunner for each run.
    :param func context_lock: A contextmgr that will be used as a lock during request handling/forking.
    :param class handler_class: The request handler class to use for each request. (Optional)
    :param bool bind_and_activate: If True, binds and activates networking at __init__ time.
                                   (Optional)
    """
    # Old-style class, so we must invoke __init__() this way.
    BaseServer.__init__(self, server_address, handler_class or PailgunHandler)
    self.socket = RecvBufferedSocket(socket.socket(self.address_family, self.socket_type))
    self.runner_factory = runner_factory
    self.allow_reuse_address = True           # Allow quick reuse of TCP_WAIT sockets.
    self.server_port = None                   # Set during server_bind() once the port is bound.
    self._context_lock = context_lock

    if bind_and_activate:
      try:
        self.server_bind()
        self.server_activate()
      except Exception:
        self.server_close()
        raise