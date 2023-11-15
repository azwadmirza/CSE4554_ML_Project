    def sync_busy(self, indicator):
        """
        Syncs the busy state with an indicator with a boolean value
        parameter.

        Arguments
        ---------
        indicator: An BooleanIndicator to sync with the busy property
        """
        if not isinstance(indicator.param.value, param.Boolean):
            raise ValueError("Busy indicator must have a value parameter"
                             "of Boolean type.")
        self._indicators.append(indicator)