    def get_extra_fields(self, model, fields):
        """Return dict of extra fields added to the historical record model"""

        user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

        def revert_url(self):
            """URL for this change in the default admin site."""
            opts = model._meta
            app_label, model_name = opts.app_label, opts.model_name
            return reverse(
                '%s:%s_%s_simple_history' % (
                    admin.site.name,
                    app_label,
                    model_name
                ),
                args=[getattr(self, opts.pk.attname), self.history_id]
            )

        def get_instance(self):
            attrs = {
                field.attname: getattr(self, field.attname)
                for field in fields.values()
            }
            if self._history_excluded_fields:
                excluded_attnames = [
                    model._meta.get_field(field).attname
                    for field in self._history_excluded_fields
                ]
                values = model.objects.filter(
                    pk=getattr(self, model._meta.pk.attname)
                ).values(*excluded_attnames).get()
                attrs.update(values)
            return model(**attrs)

        def get_next_record(self):
            """
            Get the next history record for the instance. `None` if last.
            """
            return self.instance.history.filter(
                Q(history_date__gt=self.history_date)
            ).order_by('history_date').first()

        def get_prev_record(self):
            """
            Get the previous history record for the instance. `None` if first.
            """
            return self.instance.history.filter(
                Q(history_date__lt=self.history_date)
            ).order_by('history_date').last()

        if self.history_id_field:
            history_id_field = self.history_id_field
            history_id_field.primary_key = True
            history_id_field.editable = False
        elif getattr(settings, 'SIMPLE_HISTORY_HISTORY_ID_USE_UUID', False):
            history_id_field = models.UUIDField(
                primary_key=True, default=uuid.uuid4, editable=False
            )
        else:
            history_id_field = models.AutoField(primary_key=True)

        if self.history_change_reason_field:
            # User specific field from init
            history_change_reason_field = self.history_change_reason_field
        elif getattr(
            settings, 'SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD',
            False
        ):
            # Use text field with no max length, not enforced by DB anyways
            history_change_reason_field = models.TextField(null=True)
        else:
            # Current default, with max length
            history_change_reason_field = models.CharField(
                max_length=100, null=True
            )

        return {
            'history_id': history_id_field,
            'history_date': models.DateTimeField(),
            'history_change_reason': history_change_reason_field,
            'history_user': models.ForeignKey(
                user_model, null=True, related_name=self.user_related_name,
                on_delete=models.SET_NULL),
            'history_type': models.CharField(max_length=1, choices=(
                ('+', _('Created')),
                ('~', _('Changed')),
                ('-', _('Deleted')),
            )),
            'history_object': HistoricalObjectDescriptor(
                model,
                self.fields_included(model)
            ),
            'instance': property(get_instance),
            'instance_type': model,
            'next_record': property(get_next_record),
            'prev_record': property(get_prev_record),
            'revert_url': revert_url,
            '__str__': lambda self: '%s as of %s' % (self.history_object,
                                                     self.history_date)
        }