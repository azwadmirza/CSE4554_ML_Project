    def __new__(cls, *_, **__):
        instance = object.__new__(cls)
        with cls.get_lock():  # also constructs lock if non-existent
            cls._instances.add(instance)
            # create monitoring thread
            if cls.monitor_interval and (cls.monitor is None or not
                                         cls.monitor.report()):
                try:
                    cls.monitor = TMonitor(cls, cls.monitor_interval)
                except Exception as e:  # pragma: nocover
                    warn("tqdm:disabling monitor support"
                         " (monitor_interval = 0) due to:\n" + str(e),
                         TqdmMonitorWarning, stacklevel=2)
                    cls.monitor_interval = 0
        return instance