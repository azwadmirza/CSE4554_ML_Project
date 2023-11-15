        def get_instance(self):
            return model(**{
                field.attname: getattr(self, field.attname)
                for field in fields.values()
            })