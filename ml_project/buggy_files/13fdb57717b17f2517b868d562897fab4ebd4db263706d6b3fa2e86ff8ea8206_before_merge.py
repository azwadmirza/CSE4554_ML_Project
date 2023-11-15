    def copy(self, target_table=None, **kw):
        i = Identity(
            always=self.always,
            on_null=self.on_null,
            start=self.start,
            increment=self.increment,
            minvalue=self.minvalue,
            maxvalue=self.maxvalue,
            nominvalue=self.nominvalue,
            nomaxvalue=self.nomaxvalue,
            cycle=self.cycle,
            cache=self.cache,
            order=self.order,
        )

        return self._schema_item_copy(i)