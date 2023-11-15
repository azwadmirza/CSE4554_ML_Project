    def _minutes_to_seconds(cls, val, **kwargs):
        """
        converts number of minutes to seconds
        """
        zero_value = kwargs.get("zero_value", 0)
        if val is not None:
            if val == 0:
                return zero_value
            return val * 60
        else:
            return "Not Defined"