    def _seconds_to_minutes(cls, val, **kwargs):
        """
        converts a number of seconds to minutes
        """
        zero_value = kwargs.get("zero_value", 0)
        if val is not None:
            if val == zero_value:
                return 0
            return val / 60
        else:
            return "Not Defined"