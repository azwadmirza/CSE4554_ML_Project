    def add_field(self, name, function, sampling_type, **kwargs):

        sampling_type = self._sanitize_sampling_type(
            sampling_type, kwargs.get("particle_type")
        )

        if isinstance(name, str) or not iterable(name):
            if sampling_type == "particle":
                ftype = "all"
            else:
                ftype = "gas"
            name = (ftype, name)

        override = kwargs.get("force_override", False)
        # Handle the case where the field has already been added.
        if not override and name in self:
            mylog.warning(
                "Field %s already exists. To override use `force_override=True`.", name,
            )

        return super(LocalFieldInfoContainer, self).add_field(
            name, function, sampling_type, **kwargs
        )