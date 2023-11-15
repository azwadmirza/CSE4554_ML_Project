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