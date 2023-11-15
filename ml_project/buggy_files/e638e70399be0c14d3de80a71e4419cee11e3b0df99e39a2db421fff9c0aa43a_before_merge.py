    def validate(self, value, model_instance):
        if isinstance(value, dict) and 'dependencies' in value and \
                not model_instance.managed_by_tower:
            raise django_exceptions.ValidationError(
                _("'dependencies' is not supported for custom credentials."),
                code='invalid',
                params={'value': value},
            )

        super(CredentialTypeInputField, self).validate(
            value, model_instance
        )

        ids = {}
        for field in value.get('fields', []):
            id_ = field.get('id')
            if id_ == 'tower':
                raise django_exceptions.ValidationError(
                    _('"tower" is a reserved field name'),
                    code='invalid',
                    params={'value': value},
                )

            if id_ in ids:
                raise django_exceptions.ValidationError(
                    _('field IDs must be unique (%s)' % id_),
                    code='invalid',
                    params={'value': value},
                )
            ids[id_] = True

            if 'type' not in field:
                # If no type is specified, default to string
                field['type'] = 'string'

            if field['type'] == 'become_method':
                if not model_instance.managed_by_tower:
                    raise django_exceptions.ValidationError(
                        _('become_method is a reserved type name'),
                        code='invalid',
                        params={'value': value},
                    )
                else:
                    field.pop('type')
                    field['choices'] = CHOICES_PRIVILEGE_ESCALATION_METHODS

            for key in ('choices', 'multiline', 'format', 'secret',):
                if key in field and field['type'] != 'string':
                    raise django_exceptions.ValidationError(
                        _('%s not allowed for %s type (%s)' % (key, field['type'], field['id'])),
                        code='invalid',
                        params={'value': value},
                    )