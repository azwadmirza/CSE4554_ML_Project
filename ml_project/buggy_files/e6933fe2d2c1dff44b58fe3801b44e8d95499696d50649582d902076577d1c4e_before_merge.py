    def _get_free_pos(cls, instance=None):
        """ Skips specified instance """
        try:
            return max(inst.pos for inst in cls._instances
                       if inst is not instance) + 1
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                return 0
            raise  # pragma: no cover