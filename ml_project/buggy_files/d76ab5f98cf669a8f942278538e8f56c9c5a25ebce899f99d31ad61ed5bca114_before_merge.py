    def _seconds_to_minutes(cls, val, **kwargs):
        """
        converts a number of seconds to minutes
        """
        if val is not None:
            return val / 60
        else:
            return "Not Defined"