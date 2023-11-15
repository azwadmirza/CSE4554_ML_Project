  def write(self, msg):
    msg = ensure_text(msg)
    for line in msg.rstrip().splitlines():
      # The log only accepts text, and will raise a decoding error if the default encoding is ascii
      # if provided a bytes input for unicode text.
      line = ensure_text(line)
      self._logger.log(self._log_level, line.rstrip())