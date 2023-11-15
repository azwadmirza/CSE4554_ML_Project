    def add_field(self, name, sampling_type, function=None, **kwargs):
        """
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
        units : str
           A plain text string encoding the unit.  Powers must be in
           python syntax (** instead of ^). If set to "auto" the units
           will be inferred from the return value of the field function.
        take_log : bool
           Describes whether the field should be logged
        validators : list
           A list of :class:`FieldValidator` objects
        particle_type : bool
           Is this a particle (1D) field?
        vector_field : bool
           Describes the dimensionality of the field.  Currently unused.
        display_name : str
           A name used in the plots

        """
        override = kwargs.pop("force_override", False)
        # Handle the case where the field has already been added.
        if not override and name in self:
            # See below.
            if function is None:

                def create_function(f):
                    return f

                return create_function
            return
        # add_field can be used in two different ways: it can be called
        # directly, or used as a decorator. If called directly, the
        # function will be passed in as an argument, and we simply create
        # the derived field and exit. If used as a decorator, function will
        # be None. In that case, we return a function that will be applied
        # to the function that the decorator is applied to.
        kwargs.setdefault("ds", self.ds)
        if function is None:

            def create_function(f):
                self[name] = DerivedField(name, sampling_type, f, **kwargs)
                return f

            return create_function

        if isinstance(name, tuple):
            self[name] = DerivedField(name, sampling_type, function, **kwargs)
            return

        particle_field = False
        if sampling_type == "particle":
            particle_field = True

        if kwargs.get("particle_type", False):
            warnings.warn(
                "The particle_type keyword argument of add_field has been "
                'deprecated. Please set sampling_type="particle" instead.',
                stacklevel=2,
            )
            particle_field = True

        if particle_field:
            ftype = "all"
        else:
            ftype = self.ds.default_fluid_type

        if (ftype, name) not in self:
            tuple_name = (ftype, name)
            self[tuple_name] = DerivedField(
                tuple_name, sampling_type, function, **kwargs
            )
            self.alias(name, tuple_name)
        else:
            self[name] = DerivedField(name, sampling_type, function, **kwargs)