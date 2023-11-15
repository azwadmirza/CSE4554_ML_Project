  def set_start_time(self, start_time):
    # Launch RunTracker as early as possible (before .run() is called).
    self._run_tracker = RunTracker.global_instance()
    self._reporting = Reporting.global_instance()

    self._run_start_time = start_time
    self._reporting.initialize(self._run_tracker, self._options, start_time=self._run_start_time)

    # Capture a repro of the 'before' state for this build, if needed.
    self._repro = Reproducer.global_instance().create_repro()
    if self._repro:
      self._repro.capture(self._run_tracker.run_info.get_as_dict())

    # The __call__ method of the Exiter allows for the prototype pattern.
    self._exiter = LocalExiter(self._run_tracker, self._repro, exiter=self._exiter)
    ExceptionSink.reset_exiter(self._exiter)