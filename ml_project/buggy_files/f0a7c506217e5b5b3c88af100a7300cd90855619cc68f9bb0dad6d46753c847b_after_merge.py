    def __get__(self, obj, type=None):
        if obj is None:
            return self
        field_name = self.field.name

        if field_name not in obj.__dict__:
            # Field is deferred. Fetch it from db.
            obj.refresh_from_db(fields=[field_name])
        return obj.__dict__[field_name]