  def __enter__(self):
    if not self._calls:
      self._start_time = get_cpu_clock()
    self._calls += 1