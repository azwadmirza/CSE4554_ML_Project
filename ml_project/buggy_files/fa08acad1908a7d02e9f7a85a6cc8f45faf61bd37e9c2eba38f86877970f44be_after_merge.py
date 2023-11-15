    def clone(self, data=None, shared_data=True, new_type=None, *args, **overrides):
        """Clones the object, overriding data and parameters.

        Args:
            data: New data replacing the existing data
            shared_data (bool, optional): Whether to use existing data
            new_type (optional): Type to cast object to
            *args: Additional arguments to pass to constructor
            **overrides: New keyword arguments to pass to constructor

        Returns:
            Cloned Spline
        """
        return Element2D.clone(self, data, shared_data, new_type,
                               *args, **overrides)