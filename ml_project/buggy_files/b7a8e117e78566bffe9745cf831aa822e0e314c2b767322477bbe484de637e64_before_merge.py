  def _process_session(self):
    """Process the outputs of the nailgun session."""
    try:
      for chunk_type, payload in self.iter_chunks(self._sock, return_bytes=True):
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
    finally:
      # Bad chunk types received from the server can throw NailgunProtocol.ProtocolError in
      # NailgunProtocol.iter_chunks(). This ensures the NailgunStreamWriter is always stopped.
      self._maybe_stop_input_writer()