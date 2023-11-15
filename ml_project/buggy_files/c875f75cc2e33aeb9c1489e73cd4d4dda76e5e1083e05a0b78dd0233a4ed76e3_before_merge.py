    def bulk_history_create(self, objs, batch_size=None):
        """Bulk create the history for the objects specified by objs"""

        historical_instances = [
            self.model(
                history_date=getattr(instance, '_history_date', now()),
                history_user=getattr(instance, '_history_user', None),
                **{
                    field.attname: getattr(instance, field.attname)
                    for field in instance._meta.fields
                }
            ) for instance in objs]

        return self.model.objects.bulk_create(historical_instances,
                                              batch_size=batch_size)