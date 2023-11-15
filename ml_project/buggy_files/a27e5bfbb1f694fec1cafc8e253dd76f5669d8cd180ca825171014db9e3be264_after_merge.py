  def __exit__(self, exc_type, exc_value, traceback):
    self._total = get_cpu_clock() - self._start_time
    del self._start_time