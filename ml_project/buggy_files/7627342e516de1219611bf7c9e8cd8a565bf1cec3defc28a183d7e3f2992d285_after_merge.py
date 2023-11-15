  def __init__(self, sock, in_file, out_file, err_file, exit_on_broken_pipe=False,
               remote_pid_callback=None, remote_pgrp_callback=None):
    """
    :param bool exit_on_broken_pipe: whether or not to exit when `Broken Pipe` errors are
                encountered
    :param remote_pid_callback: Callback to run when a pid chunk is received from a remote client.
    :param remote_pgrp_callback: Callback to run when a pgrp (process group) chunk is received from
                                 a remote client.
    """
    self._sock = sock
    self._input_writer = None if not in_file else NailgunStreamWriter(
      (in_file.fileno(),),
      self._sock,
      (ChunkType.STDIN,),
      ChunkType.STDIN_EOF
    )
    self._stdout = out_file
    self._stderr = err_file
    self._exit_on_broken_pipe = exit_on_broken_pipe
    self.remote_pid = None
    self.remote_process_cmdline = None
    self.remote_pgrp = None
    self._remote_pid_callback = remote_pid_callback
    self._remote_pgrp_callback = remote_pgrp_callback
    # NB: These variables are set in a signal handler to implement graceful shutdown.
    self._exit_timeout_start_time = None
    self._exit_timeout = None
    self._exit_reason = None