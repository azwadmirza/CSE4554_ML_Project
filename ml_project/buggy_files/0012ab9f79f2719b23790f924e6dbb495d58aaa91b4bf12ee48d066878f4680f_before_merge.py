  def __enter__(self):
    if not self._calls:
      self._start_time = time.clock()
    self._calls += 1