    def _validate_internal_indices(self, mode=None, **kwargs):
        """
        Validates and optionally updates internal and external indices
        of modin_frame in specified mode. There is 3 modes supported:
            1. "reduced" - validates and updates indices on that axes
                where external indices is ["__reduced__"]
            2. "all" - validates indices at all axes, optionally updates
                internal indices if `update` parameter specified in kwargs
            3. "custom" - validation follows arguments specified in kwargs.

        Parameters
        ----------
            mode : str or bool, default None
            validate_index : bool, (optional, could be specified via `mode`)
            validate_columns : bool, (optional, could be specified via `mode`)
        """

        if isinstance(mode, bool):
            mode = "all"

        reduced_sample = pandas.Index(["__reduced__"])
        args_dict = {
            "custom": kwargs,
            "reduced": {
                "validate_index": self.index.equals(reduced_sample),
                "validate_columns": self.columns.equals(reduced_sample),
            },
            "all": {"validate_index": True, "validate_columns": True},
        }

        args = args_dict.get(mode, args_dict["custom"])

        if args.get("validate_index", True):
            self._validate_axis_equality(axis=0)
        if args.get("validate_columns", True):
            self._validate_axis_equality(axis=1)