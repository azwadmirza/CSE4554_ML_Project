    def add_field(self, name, function, sampling_type, **kwargs):
        """
        Dataset-specific call to add_field

        Add a new field, along with supplemental metadata, to the list of
        available fields.  This respects a number of arguments, all of which
        are passed on to the constructor for
        :class:`~yt.data_objects.api.DerivedField`.

        Parameters
        ----------

        name : str
           is the name of the field.
        function : callable
           A function handle that defines the field.  Should accept
           arguments (field, data)
        sampling_type: str
           "cell" or "particle" or "local"
        units : str
           A plain text string encoding the unit.  Powers must be in
           python syntax (** instead of ^).
        take_log : bool
           Describes whether the field should be logged
        validators : list
           A list of :class:`FieldValidator` objects
        vector_field : bool
           Describes the dimensionality of the field.  Currently unused.
        display_name : str
           A name used in the plots
        force_override : bool
           Whether to override an existing derived field. Does not work with
           on-disk fields.

        """
        self.index
        override = kwargs.get("force_override", False)
        if override and name in self.index.field_list:
            raise RuntimeError(
                "force_override is only meant to be used with "
                "derived fields, not on-disk fields."
            )
        # Handle the case where the field has already been added.
        if not override and name in self.field_info:
            mylog.warning(
                "Field %s already exists. To override use `force_override=True`.", name,
            )

        self.field_info.add_field(name, function, sampling_type, **kwargs)
        self.field_info._show_field_errors.append(name)
        deps, _ = self.field_info.check_derived_fields([name])
        self.field_dependencies.update(deps)