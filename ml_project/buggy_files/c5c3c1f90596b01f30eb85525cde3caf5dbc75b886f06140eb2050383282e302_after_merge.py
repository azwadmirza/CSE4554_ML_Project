    async def _prefetch_m2m_relation(self, instance_list: list, field: str, related_query) -> list:
        instance_id_set = {
            self._field_to_db(instance._meta.pk, instance.pk, instance)
            for instance in instance_list
        }  # type: Set[Any]

        field_object = self.model._meta.fields_map[field]

        through_table = Table(field_object.through)

        subquery = (
            self.db.query_class.from_(through_table)
            .select(
                getattr(through_table, field_object.backward_key).as_("_backward_relation_key"),
                getattr(through_table, field_object.forward_key).as_("_forward_relation_key"),
            )
            .where(getattr(through_table, field_object.backward_key).isin(instance_id_set))
        )

        related_query_table = Table(related_query.model._meta.table)
        related_pk_field = related_query.model._meta.db_pk_field
        query = (
            related_query.query.join(subquery)
            .on(subquery._forward_relation_key == getattr(related_query_table, related_pk_field))
            .select(
                subquery._backward_relation_key.as_("_backward_relation_key"),
                *[getattr(related_query_table, field).as_(field) for field in related_query.fields],
            )
        )

        if related_query._q_objects:
            joined_tables = []  # type: List[Table]
            modifier = QueryModifier()
            for node in related_query._q_objects:
                modifier &= node.resolve(
                    model=related_query.model,
                    annotations=related_query._annotations,
                    custom_filters=related_query._custom_filters,
                )

            where_criterion, joins, having_criterion = modifier.get_query_modifiers()
            for join in joins:
                if join[0] not in joined_tables:
                    query = query.join(join[0], how=JoinType.left_outer).on(join[1])
                    joined_tables.append(join[0])

            if where_criterion:
                query = query.where(where_criterion)

            if having_criterion:
                query = query.having(having_criterion)

        raw_results = await self.db.execute_query(query.get_sql())
        relations = {
            (
                self.model._meta.pk.to_python_value(e["_backward_relation_key"]),
                field_object.type._meta.pk.to_python_value(e[related_pk_field]),
            )
            for e in raw_results
        }
        related_object_list = [related_query.model._init_from_db(**e) for e in raw_results]
        await self.__class__(
            model=related_query.model, db=self.db, prefetch_map=related_query._prefetch_map
        ).fetch_for_list(related_object_list)
        related_object_map = {e.pk: e for e in related_object_list}
        relation_map = {}  # type: Dict[str, list]

        for object_id, related_object_id in relations:
            if object_id not in relation_map:
                relation_map[object_id] = []
            relation_map[object_id].append(related_object_map[related_object_id])

        for instance in instance_list:
            relation_container = getattr(instance, field)
            relation_container._set_result_for_query(relation_map.get(instance.pk, []))
        return instance_list