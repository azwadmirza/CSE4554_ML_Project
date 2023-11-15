    async def add(self, *instances, using_db=None) -> None:
        """
        Adds one or more of ``instances`` to the relation.

        If it is already added, it will be silently ignored.
        """
        if not instances:
            return
        if self.instance.pk is None:
            raise OperationalError(
                "You should first call .save() on {model}".format(model=self.instance)
            )
        db = using_db if using_db else self.model._meta.db
        pk_formatting_func = type(self.instance)._meta.pk.to_db_value
        related_pk_formatting_func = type(instances[0])._meta.pk.to_db_value
        through_table = Table(self.field.through)
        select_query = (
            db.query_class.from_(through_table)
            .where(
                getattr(through_table, self.field.backward_key)
                == pk_formatting_func(self.instance.pk, self.instance)
            )
            .select(self.field.backward_key, self.field.forward_key)
        )
        query = db.query_class.into(through_table).columns(
            getattr(through_table, self.field.forward_key),
            getattr(through_table, self.field.backward_key),
        )

        if len(instances) == 1:
            criterion = getattr(
                through_table, self.field.forward_key
            ) == related_pk_formatting_func(instances[0].pk, instances[0])
        else:
            criterion = getattr(through_table, self.field.forward_key).isin(
                [related_pk_formatting_func(i.pk, i) for i in instances]
            )

        select_query = select_query.where(criterion)

        already_existing_relations_raw = await db.execute_query(str(select_query))
        already_existing_relations = {
            (r[self.field.backward_key], r[self.field.forward_key])
            for r in already_existing_relations_raw
        }

        insert_is_required = False
        for instance_to_add in instances:
            if instance_to_add.pk is None:
                raise OperationalError(
                    "You should first call .save() on {model}".format(model=instance_to_add)
                )
            if (self.instance.pk, instance_to_add.pk) in already_existing_relations:
                continue
            query = query.insert(
                related_pk_formatting_func(instance_to_add.pk, instance_to_add),
                pk_formatting_func(self.instance.pk, self.instance),
            )
            insert_is_required = True
        if insert_is_required:
            await db.execute_query(str(query))