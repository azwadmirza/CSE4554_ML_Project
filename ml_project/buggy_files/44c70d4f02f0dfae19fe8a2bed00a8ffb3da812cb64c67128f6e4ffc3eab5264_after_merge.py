    def new_with_restriction(
        self,
        entities: Union[None, Collection[int], Collection[str]] = None,
        relations: Union[None, Collection[int], Collection[str]] = None,
        invert_entity_selection: bool = False,
        invert_relation_selection: bool = False,
    ) -> 'TriplesFactory':
        """Make a new triples factory only keeping the given entities and relations, but keeping the ID mapping.

        :param entities:
            The entities of interest. If None, defaults to all entities.
        :param relations:
            The relations of interest. If None, defaults to all relations.
        :param invert_entity_selection:
            Whether to invert the entity selection, i.e. select those triples without the provided entities.
        :param invert_relation_selection:
            Whether to invert the relation selection, i.e. select those triples without the provided relations.

        :return:
            A new triples factory, which has only a subset of the triples containing the entities and relations of
            interest. The label-to-ID mapping is *not* modified.
        """
        keep_mask = None

        # Filter for entities
        if entities is not None:
            keep_mask = self.get_mask_for_entities(entities=entities, invert=invert_entity_selection)
            remaining_entities = self.num_entities - len(entities) if invert_entity_selection else len(entities)
            logger.info(f"keeping {format_relative_comparison(remaining_entities, self.num_entities)} entities.")

        # Filter for relations
        if relations is not None:
            relation_mask = self.get_mask_for_relations(relations=relations, invert=invert_relation_selection)
            remaining_relations = self.num_relations - len(relations) if invert_entity_selection else len(relations)
            logger.info(f"keeping {format_relative_comparison(remaining_relations, self.num_relations)} relations.")
            keep_mask = relation_mask if keep_mask is None else keep_mask & relation_mask

        # No filtering happened
        if keep_mask is None:
            return self

        num_triples = keep_mask.sum()
        logger.info(f"keeping {format_relative_comparison(num_triples, self.num_triples)} triples.")
        return self.clone_and_exchange_triples(mapped_triples=self.mapped_triples[keep_mask])