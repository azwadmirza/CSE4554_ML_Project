  def process_request(self, request, client_address):
    """Override of TCPServer.process_request() that provides for forking request handlers and
    delegates error handling to the request handler."""
    # Instantiate the request handler.
    handler = self.RequestHandlerClass(request, client_address, self)

    try:
      # Attempt to handle a request with the handler.
      handler.handle_request()
    except Exception as e:
      # If that fails, (synchronously) handle the error with the error handler sans-fork.
      try:
        handler.handle_error(e)
      finally:
        # Shutdown the socket since we don't expect a fork() in the exception context.
        self.shutdown_request(request)
    else:
      # At this point, we expect a fork() has taken place - the parent side will return, and so we
      # close the request here from the parent without explicitly shutting down the socket. The
      # child half of this will perform an os._exit() before it gets to this point and is also
      # responsible for shutdown and closing of the socket when its execution is complete.
      self.close_request(request)