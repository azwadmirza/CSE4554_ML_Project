    def clean(self):

        # Validate that termination A exists
        if not hasattr(self, 'termination_a_type'):
            raise ValidationError('Termination A type has not been specified')
        try:
            self.termination_a_type.model_class().objects.get(pk=self.termination_a_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_a': 'Invalid ID for type {}'.format(self.termination_a_type)
            })

        # Validate that termination B exists
        if not hasattr(self, 'termination_b_type'):
            raise ValidationError('Termination B type has not been specified')
        try:
            self.termination_b_type.model_class().objects.get(pk=self.termination_b_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_b': 'Invalid ID for type {}'.format(self.termination_b_type)
            })

        # If editing an existing Cable instance, check that neither termination has been modified.
        if self.pk:
            err_msg = 'Cable termination points may not be modified. Delete and recreate the cable instead.'
            if (
                self.termination_a_type != self._orig_termination_a_type or
                self.termination_a_id != self._orig_termination_a_id
            ):
                raise ValidationError({
                    'termination_a': err_msg
                })
            if (
                self.termination_b_type != self._orig_termination_b_type or
                self.termination_b_id != self._orig_termination_b_id
            ):
                raise ValidationError({
                    'termination_b': err_msg
                })

        type_a = self.termination_a_type.model
        type_b = self.termination_b_type.model

        # Validate interface types
        if type_a == 'interface' and self.termination_a.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_a_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_a.get_type_display()
                )
            })
        if type_b == 'interface' and self.termination_b.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_b_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_b.get_type_display()
                )
            })

        # Check that termination types are compatible
        if type_b not in COMPATIBLE_TERMINATION_TYPES.get(type_a):
            raise ValidationError("Incompatible termination types: {} and {}".format(
                self.termination_a_type, self.termination_b_type
            ))

        # A RearPort with multiple positions must be connected to a component with an equal number of positions
        if isinstance(self.termination_a, RearPort) and isinstance(self.termination_b, RearPort):
            if self.termination_a.positions != self.termination_b.positions:
                raise ValidationError(
                    "{} has {} positions and {} has {}. Both terminations must have the same number of positions.".format(
                        self.termination_a, self.termination_a.positions,
                        self.termination_b, self.termination_b.positions
                    )
                )

        # A termination point cannot be connected to itself
        if self.termination_a == self.termination_b:
            raise ValidationError("Cannot connect {} to itself".format(self.termination_a_type))

        # A front port cannot be connected to its corresponding rear port
        if (
            type_a in ['frontport', 'rearport'] and
            type_b in ['frontport', 'rearport'] and
            (
                getattr(self.termination_a, 'rear_port', None) == self.termination_b or
                getattr(self.termination_b, 'rear_port', None) == self.termination_a
            )
        ):
            raise ValidationError("A front port cannot be connected to it corresponding rear port")

        # Check for an existing Cable connected to either termination object
        if self.termination_a.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_a, self.termination_a.cable_id
            ))
        if self.termination_b.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_b, self.termination_b.cable_id
            ))

        # Validate length and length_unit
        if self.length is not None and not self.length_unit:
            raise ValidationError("Must specify a unit when setting a cable length")
        elif self.length is None:
            self.length_unit = ''