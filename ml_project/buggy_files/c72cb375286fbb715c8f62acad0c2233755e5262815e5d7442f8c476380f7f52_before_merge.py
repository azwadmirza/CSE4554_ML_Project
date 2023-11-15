    def _validate_units(self, units):
        """
        Validates the astropy unit-information associated with a TimeSeries.
        Should be a dictionary of some form (but not MetaDict) with only
        astropy units for values.
        """

        warnings.simplefilter('always', Warning)
        result = True

        # It must be a dictionary
        if not isinstance(units, dict) or isinstance(units, MetaDict):
            return False

        for key in units:
            if not isinstance(units[key], u.UnitBase):
                # If this is not a unit then this can't be a valid units dict.
                return False

        # Passed all the tests
        return result