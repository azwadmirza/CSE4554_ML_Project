    def _minutes_to_seconds(cls, val, **kwargs):
        """
        converts number of minutes to seconds
        """
        if val is not None:
            return val * 60
        else:
            return "Not Defined"