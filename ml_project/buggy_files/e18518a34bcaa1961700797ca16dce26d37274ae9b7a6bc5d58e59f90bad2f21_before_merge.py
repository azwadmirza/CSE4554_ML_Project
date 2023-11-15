    def __new__(cls, *args, **kwargs):
        # Create a new instance
        instance = object.__new__(cls)
        # Add to the list of instances
        if "_instances" not in cls.__dict__:
            cls._instances = WeakSet()
        if "_lock" not in cls.__dict__:
            cls._lock = TqdmDefaultWriteLock()
        with cls._lock:
            cls._instances.add(instance)
        # Create the monitoring thread
        if cls.monitor_interval and (cls.monitor is None or not
                                     cls.monitor.report()):
            try:
                cls.monitor = TMonitor(cls, cls.monitor_interval)
            except Exception as e:  # pragma: nocover
                from warnings import warn
                warn("tqdm:disabling monitor support"
                     " (monitor_interval = 0) due to:\n" + str(e),
                     RuntimeWarning)
                cls.monitor_interval = 0
        # Return the instance
        return instance