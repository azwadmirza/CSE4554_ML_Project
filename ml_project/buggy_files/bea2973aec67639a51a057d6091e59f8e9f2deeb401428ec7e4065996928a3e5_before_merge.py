  def write(self, msg):
    msg = ensure_text(msg)
    for line in msg.rstrip().splitlines():
      self._logger.log(self._log_level, line.rstrip())