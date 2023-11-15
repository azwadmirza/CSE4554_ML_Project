    def _decr_instances(cls, instance):
        """
        Remove from list and reposition other bars
        so that newer bars won't overlap previous bars
        """
        try:  # in case instance was explicitly positioned, it won't be in set
            cls._instances.remove(instance)
            for inst in cls._instances:
                if inst.pos > instance.pos:
                    inst.pos -= 1
            # Kill monitor if no instances are left
            if not cls._instances and cls.monitor:
                cls.monitor.exit()
                try:
                    del cls.monitor
                except AttributeError:
                    pass
                cls.monitor = None
        except KeyError:
            pass