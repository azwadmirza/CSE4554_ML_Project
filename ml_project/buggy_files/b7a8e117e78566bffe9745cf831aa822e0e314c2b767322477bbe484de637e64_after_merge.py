  def _process_session(self):
    """Process the outputs of the nailgun session.

    :raises: :class:`NailgunProtocol.ProcessStreamTimeout` if a timeout set from a signal handler
                                                           with .set_exit_timeout() completes.
    :raises: :class:`Exception` if the session completes before the timeout, the `reason` argument
                                to .set_exit_timeout() will be raised."""
    try:
      for chunk_type, payload in self.iter_chunks(self._sock, return_bytes=True,
                                                  timeout_object=self):
        # TODO(#6579): assert that we have at this point received all the chunk types in
        # ChunkType.REQUEST_TYPES, then require PID and PGRP (exactly once?), and then allow any of
        # ChunkType.EXECUTION_TYPES.
        if chunk_type == ChunkType.STDOUT:
          self._write_flush(self._stdout, payload)
        elif chunk_type == ChunkType.STDERR:
          self._write_flush(self._stderr, payload)
        elif chunk_type == ChunkType.EXIT:
          self._write_flush(self._stdout)
          self._write_flush(self._stderr)
          return int(payload)
        elif chunk_type == ChunkType.PID:
          self.remote_pid = int(payload)
          self.remote_process_cmdline = psutil.Process(self.remote_pid).cmdline()
          if self._remote_pid_callback:
            self._remote_pid_callback(self.remote_pid)
        elif chunk_type == ChunkType.PGRP:
          self.remote_pgrp = int(payload)
          if self._remote_pgrp_callback:
            self._remote_pgrp_callback(self.remote_pgrp)
        elif chunk_type == ChunkType.START_READING_INPUT:
          self._maybe_start_input_writer()
        else:
          raise self.ProtocolError('received unexpected chunk {} -> {}'.format(chunk_type, payload))
    except NailgunProtocol.ProcessStreamTimeout as e:
      assert(self.remote_pid is not None)
      # NB: We overwrite the process title in the pantsd-runner process, which causes it to have an
      # argv with lots of empty spaces for some reason. We filter those out and pretty-print the
      # rest here.
      filtered_remote_cmdline = safe_shlex_join(
        arg for arg in self.remote_process_cmdline if arg != '')
      logger.warning(
        "timed out when attempting to gracefully shut down the remote client executing \"{}\". "
        "sending SIGKILL to the remote client at pid: {}. message: {}"
        .format(filtered_remote_cmdline, self.remote_pid, e))
    finally:
      # Bad chunk types received from the server can throw NailgunProtocol.ProtocolError in
      # NailgunProtocol.iter_chunks(). This ensures the NailgunStreamWriter is always stopped.
      self._maybe_stop_input_writer()
      # If an asynchronous error was set at any point (such as in a signal handler), we want to make
      # sure we clean up the remote process before exiting with error.
      if self._exit_reason:
        if self.remote_pgrp:
          safe_kill(self.remote_pgrp, signal.SIGKILL)
        if self.remote_pid:
          safe_kill(self.remote_pid, signal.SIGKILL)
        raise self._exit_reason