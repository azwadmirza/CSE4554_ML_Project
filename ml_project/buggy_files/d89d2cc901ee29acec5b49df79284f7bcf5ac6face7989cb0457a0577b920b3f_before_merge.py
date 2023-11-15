    def post(self, request, **kwargs):

        model = self.queryset.model

        # Create a mutable copy of the POST data
        post_data = request.POST.copy()

        # If we are editing *all* objects in the queryset, replace the PK list with all matched objects.
        if post_data.get('_all') and self.filterset is not None:
            post_data['pk'] = [obj.pk for obj in self.filterset(request.GET, model.objects.only('pk')).qs]

        if '_apply' in request.POST:
            form = self.form(model, request.POST)
            if form.is_valid():

                custom_fields = form.custom_fields if hasattr(form, 'custom_fields') else []
                standard_fields = [
                    field for field in form.fields if field not in custom_fields + ['pk']
                ]
                nullified_fields = request.POST.getlist('_nullify')

                try:

                    with transaction.atomic():

                        updated_count = 0
                        for obj in model.objects.filter(pk__in=form.cleaned_data['pk']):

                            # Update standard fields. If a field is listed in _nullify, delete its value.
                            for name in standard_fields:

                                try:
                                    model_field = model._meta.get_field(name)
                                except FieldDoesNotExist:
                                    # This form field is used to modify a field rather than set its value directly
                                    model_field = None

                                # Handle nullification
                                if name in form.nullable_fields and name in nullified_fields:
                                    if isinstance(model_field, ManyToManyField):
                                        getattr(obj, name).set([])
                                    else:
                                        setattr(obj, name, None if model_field.null else '')

                                # ManyToManyFields
                                elif isinstance(model_field, ManyToManyField):
                                    getattr(obj, name).set(form.cleaned_data[name])

                                # Normal fields
                                elif form.cleaned_data[name] not in (None, ''):
                                    setattr(obj, name, form.cleaned_data[name])

                            obj.full_clean()
                            obj.save()

                            # Update custom fields
                            obj_type = ContentType.objects.get_for_model(model)
                            for name in custom_fields:
                                field = form.fields[name].model
                                if name in form.nullable_fields and name in nullified_fields:
                                    CustomFieldValue.objects.filter(
                                        field=field, obj_type=obj_type, obj_id=obj.pk
                                    ).delete()
                                elif form.cleaned_data[name] not in [None, '']:
                                    try:
                                        cfv = CustomFieldValue.objects.get(
                                            field=field, obj_type=obj_type, obj_id=obj.pk
                                        )
                                    except CustomFieldValue.DoesNotExist:
                                        cfv = CustomFieldValue(
                                            field=field, obj_type=obj_type, obj_id=obj.pk
                                        )
                                    cfv.value = form.cleaned_data[name]
                                    cfv.save()

                            # Add/remove tags
                            if form.cleaned_data.get('add_tags', None):
                                obj.tags.add(*form.cleaned_data['add_tags'])
                            if form.cleaned_data.get('remove_tags', None):
                                obj.tags.remove(*form.cleaned_data['remove_tags'])

                            updated_count += 1

                    if updated_count:
                        msg = 'Updated {} {}'.format(updated_count, model._meta.verbose_name_plural)
                        messages.success(self.request, msg)

                    return redirect(self.get_return_url(request))

                except ValidationError as e:
                    messages.error(self.request, "{} failed validation: {}".format(obj, e))

        else:
            # Pass the PK list as initial data to avoid binding the form
            initial_data = querydict_to_dict(post_data)
            form = self.form(model, initial=initial_data)

        # Retrieve objects being edited
        table = self.table(self.queryset.filter(pk__in=post_data.getlist('pk')), orderable=False)
        if not table.rows:
            messages.warning(request, "No {} were selected.".format(model._meta.verbose_name_plural))
            return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'form': form,
            'table': table,
            'obj_type_plural': model._meta.verbose_name_plural,
            'return_url': self.get_return_url(request),
        })