    def _validate_internal_indices(self, mode=None, **kwargs):
        """
        Validates and optionally updates internal and external indices
        of modin_frame in specified mode. There is 3 modes supported:
            1. "reduced" - force validates on that axes
                where external indices is ["__reduced__"]
            2. "all" - validates indices at all axes, optionally force
                if `force` parameter specified in kwargs
            3. "custom" - validation follows arguments specified in kwargs.

        Parameters
        ----------
            mode : str or bool, default None
            validate_index : bool, (optional, could be specified via `mode`)
            validate_columns : bool, (optional, could be specified via `mode`)
            force : bool (optional, could be specified via `mode`)
                Whether to update external indices with internal if their lengths
                do not match or raise an exception in that case.
        """

        if isinstance(mode, bool):
            is_force = mode
            mode = "all"
        else:
            is_force = kwargs.get("force", False)

        reduced_sample = pandas.Index(["__reduced__"])
        args_dict = {
            "custom": kwargs,
            "reduced": {
                "validate_index": self.index.equals(reduced_sample),
                "validate_columns": self.columns.equals(reduced_sample),
                "force": True,
            },
            "all": {
                "validate_index": True,
                "validate_columns": True,
                "force": is_force,
            },
        }

        args = args_dict.get(mode, args_dict["custom"])

        if args.get("validate_index", True):
            self._validate_axis_equality(axis=0)
        if args.get("validate_columns", True):
            self._validate_axis_equality(axis=1)