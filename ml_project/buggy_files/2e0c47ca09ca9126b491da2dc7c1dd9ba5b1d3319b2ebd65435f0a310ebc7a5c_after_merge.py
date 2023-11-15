    def _accept_or_ignore_job_kwargs(self, **kwargs):
        exclude_errors = kwargs.pop('_exclude_errors', [])
        prompted_data = {}
        rejected_data = {}
        accepted_vars, rejected_vars, errors_dict = self.accept_or_ignore_variables(
            kwargs.get('extra_vars', {}),
            _exclude_errors=exclude_errors,
            extra_passwords=kwargs.get('survey_passwords', {}))
        if accepted_vars:
            prompted_data['extra_vars'] = accepted_vars
        if rejected_vars:
            rejected_data['extra_vars'] = rejected_vars

        # Handle all the other fields that follow the simple prompting rule
        for field_name, ask_field_name in self.get_ask_mapping().items():
            if field_name not in kwargs or field_name == 'extra_vars' or kwargs[field_name] is None:
                continue

            new_value = kwargs[field_name]
            old_value = getattr(self, field_name)

            field = self._meta.get_field(field_name)
            if isinstance(field, models.ManyToManyField):
                old_value = set(old_value.all())
                if getattr(self, '_deprecated_credential_launch', False):
                    # TODO: remove this code branch when support for `extra_credentials` goes away
                    new_value = set(kwargs[field_name])
                else:
                    new_value = set(kwargs[field_name]) - old_value
                    if not new_value:
                        continue

            if new_value == old_value:
                # no-op case: Fields the same as template's value
                # counted as neither accepted or ignored
                continue
            elif getattr(self, ask_field_name):
                # accepted prompt
                prompted_data[field_name] = new_value
            else:
                # unprompted - template is not configured to accept field on launch
                rejected_data[field_name] = new_value
                # Not considered an error for manual launch, to support old
                # behavior of putting them in ignored_fields and launching anyway
                if 'prompts' not in exclude_errors:
                    errors_dict[field_name] = _('Field is not configured to prompt on launch.').format(field_name=field_name)

        if ('prompts' not in exclude_errors and
                (not getattr(self, 'ask_credential_on_launch', False)) and
                self.passwords_needed_to_start):
            errors_dict['passwords_needed_to_start'] = _(
                'Saved launch configurations cannot provide passwords needed to start.')

        needed = self.resources_needed_to_start
        if needed:
            needed_errors = []
            for resource in needed:
                if resource in prompted_data:
                    continue
                needed_errors.append(_("Job Template {} is missing or undefined.").format(resource))
            if needed_errors:
                errors_dict['resources_needed_to_start'] = needed_errors

        return prompted_data, rejected_data, errors_dict