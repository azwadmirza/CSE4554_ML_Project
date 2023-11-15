    def _decr_instances(cls, instance):
        """
        Remove from list and reposition other bars
        so that newer bars won't overlap previous bars
        """
        with cls._lock:
            try:
                cls._instances.remove(instance)
            except KeyError:
                if not instance.gui:  # pragma: no cover
                    raise
            else:
                for inst in cls._instances:
                    # negative `pos` means fixed
                    if inst.pos > abs(instance.pos):
                        inst.pos -= 1
                        # TODO: check this doesn't overwrite another fixed bar
        # Kill monitor if no instances are left
        if not cls._instances and cls.monitor:
            try:
                cls.monitor.exit()
                del cls.monitor
            except AttributeError:  # pragma: nocover
                pass
            else:
                cls.monitor = None