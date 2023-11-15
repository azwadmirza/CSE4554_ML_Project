    async def _prefetch_reverse_relation(
        self, instance_list: list, field: str, related_query
    ) -> list:
        instance_id_set = {instance.pk for instance in instance_list}  # type: Set[Any]
        backward_relation_manager = getattr(self.model, field)
        relation_field = backward_relation_manager.relation_field

        related_object_list = await related_query.filter(
            **{"{}__in".format(relation_field): list(instance_id_set)}
        )

        related_object_map = {}  # type: Dict[str, list]
        for entry in related_object_list:
            object_id = getattr(entry, relation_field)
            if object_id in related_object_map.keys():
                related_object_map[object_id].append(entry)
            else:
                related_object_map[object_id] = [entry]
        for instance in instance_list:
            relation_container = getattr(instance, field)
            relation_container._set_result_for_query(related_object_map.get(instance.pk, []))
        return instance_list