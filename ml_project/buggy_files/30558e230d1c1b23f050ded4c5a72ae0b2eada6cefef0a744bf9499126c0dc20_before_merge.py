    def add_field(self, name, function=None, sampling_type=None, **kwargs):
        if not isinstance(name, tuple):
            if kwargs.setdefault("particle_type", False):
                name = ("all", name)
            else:
                name = ("gas", name)
        override = kwargs.get("force_override", False)
        # Handle the case where the field has already been added.
        if not override and name in self:
            mylog.error(
                "Field %s already exists. To override use " + "force_override=True.",
                name,
            )
        if kwargs.setdefault("particle_type", False):
            if sampling_type is not None and sampling_type != "particle":
                raise RuntimeError(
                    "Clashing definition of 'sampling_type' and "
                    "'particle_type'. Note that 'particle_type' is "
                    "deprecated. Please just use 'sampling_type'."
                )
            else:
                sampling_type = "particle"
        if sampling_type is None:
            warnings.warn(
                "Because 'sampling_type' is not specified, yt will "
                "assume a 'cell' sampling_type for the %s field" % (name,),
                stacklevel=3,
            )
            sampling_type = "cell"
        return super(LocalFieldInfoContainer, self).add_field(
            name, sampling_type, function, **kwargs
        )