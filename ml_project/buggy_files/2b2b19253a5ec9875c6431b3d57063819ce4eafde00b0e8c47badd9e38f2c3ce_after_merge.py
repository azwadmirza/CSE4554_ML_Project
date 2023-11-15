    def establish_variables(self, data, **kws):
        """Extract variables from data or use directly."""
        self.data = data

        # Validate the inputs
        any_strings = any([isinstance(v, string_types) for v in kws.values()])
        if any_strings and data is None:
            raise ValueError("Must pass `data` if using named variables.")

        # Set the variables
        for var, val in kws.items():
            if isinstance(val, string_types):
                setattr(self, var, data[val])
            elif isinstance(val, list):
                setattr(self, var, np.asarray(val))
            else:
                setattr(self, var, val)