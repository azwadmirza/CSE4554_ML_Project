    def validate(self, value, model_instance):
        super(CredentialTypeInjectorField, self).validate(
            value, model_instance
        )

        # make sure the inputs are valid first
        try:
            CredentialTypeInputField().validate(model_instance.inputs, model_instance)
        except django_exceptions.ValidationError:
            # If `model_instance.inputs` itself is invalid, we can't make an
            # estimation as to whether our Jinja templates contain valid field
            # names; don't continue
            return

        # In addition to basic schema validation, search the injector fields
        # for template variables and make sure they match the fields defined in
        # the inputs
        valid_namespace = dict(
            (field, 'EXAMPLE')
            for field in model_instance.defined_fields
        )

        class TowerNamespace:
            filename = None
        valid_namespace['tower'] = TowerNamespace()

        # ensure either single file or multi-file syntax is used (but not both)
        template_names = [x for x in value.get('file', {}).keys() if x.startswith('template')]
        if 'template' in template_names and len(template_names) > 1:
            raise django_exceptions.ValidationError(
                _('Must use multi-file syntax when injecting multiple files'),
                code='invalid',
                params={'value': value},
            )
        if 'template' not in template_names:
            valid_namespace['tower'].filename = TowerNamespace()
            for template_name in template_names:
                template_name = template_name.split('.')[1]
                setattr(valid_namespace['tower'].filename, template_name, 'EXAMPLE')

        for type_, injector in value.items():
            for key, tmpl in injector.items():
                try:
                    Environment(
                        undefined=StrictUndefined
                    ).from_string(tmpl).render(valid_namespace)
                except UndefinedError as e:
                    raise django_exceptions.ValidationError(
                        _('{sub_key} uses an undefined field ({error_msg})').format(
                            sub_key=key, error_msg=e),
                        code='invalid',
                        params={'value': value},
                    )
                except TemplateSyntaxError as e:
                    raise django_exceptions.ValidationError(
                        _('Syntax error rendering template for {sub_key} inside of {type} ({error_msg})').format(
                            sub_key=key, type=type_, error_msg=e),
                        code='invalid',
                        params={'value': value},
                    )