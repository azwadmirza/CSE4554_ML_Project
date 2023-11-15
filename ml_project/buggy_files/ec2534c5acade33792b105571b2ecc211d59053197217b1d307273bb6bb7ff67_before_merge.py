    def _query(self):
        if not self.instance.pk:
            raise OperationalError(
                "This objects hasn't been instanced, call .save() before" " calling related queries"
            )
        return self.model.filter(**{self.relation_field: self.instance.pk})