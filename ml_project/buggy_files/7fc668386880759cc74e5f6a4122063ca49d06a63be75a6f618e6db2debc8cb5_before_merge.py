    def __new__(cls, *_, **__):
        # Create a new instance
        instance = object.__new__(cls)
        # Construct the lock if it does not exist
        with cls.get_lock():
            # Add to the list of instances
            if not hasattr(cls, '_instances'):
                cls._instances = WeakSet()
            cls._instances.add(instance)
            # Create the monitoring thread
            if cls.monitor_interval and (cls.monitor is None or not
                                         cls.monitor.report()):
                try:
                    cls.monitor = TMonitor(cls, cls.monitor_interval)
                except Exception as e:  # pragma: nocover
                    warn("tqdm:disabling monitor support"
                         " (monitor_interval = 0) due to:\n" + str(e),
                         TqdmMonitorWarning, stacklevel=2)
                    cls.monitor_interval = 0
        # Return the instance
        return instance