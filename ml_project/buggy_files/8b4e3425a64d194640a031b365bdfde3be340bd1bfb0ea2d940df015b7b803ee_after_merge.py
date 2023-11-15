  def iter_chunks(cls, sock, return_bytes=False, timeout_object=None):
    """Generates chunks from a connected socket until an Exit chunk is sent or a timeout occurs.

    :param sock: the socket to read from.
    :param bool return_bytes: If False, decode the payload into a utf-8 string.
    :param cls.TimeoutProvider timeout_object: If provided, will be checked every iteration for a
                                               possible timeout.
    :raises: :class:`cls.ProcessStreamTimeout`
    """
    assert(timeout_object is None or isinstance(timeout_object, cls.TimeoutProvider))
    orig_timeout_time = None
    timeout_interval = None
    while 1:
      if orig_timeout_time is not None:
        remaining_time = time.time() - (orig_timeout_time + timeout_interval)
        if remaining_time > 0:
          original_timestamp = datetime.datetime.fromtimestamp(orig_timeout_time).isoformat()
          raise cls.ProcessStreamTimeout(
            "iterating over bytes from nailgun timed out with timeout interval {} starting at {}, "
            "overtime seconds: {}"
            .format(timeout_interval, original_timestamp, remaining_time))
      elif timeout_object is not None:
        opts = timeout_object.maybe_timeout_options()
        if opts:
          orig_timeout_time = opts.start_time
          timeout_interval = opts.interval
          continue
        remaining_time = None
      else:
        remaining_time = None

      with cls._set_socket_timeout(sock, timeout=remaining_time):
        chunk_type, payload = cls.read_chunk(sock, return_bytes)
        yield chunk_type, payload
        if chunk_type == ChunkType.EXIT:
          break