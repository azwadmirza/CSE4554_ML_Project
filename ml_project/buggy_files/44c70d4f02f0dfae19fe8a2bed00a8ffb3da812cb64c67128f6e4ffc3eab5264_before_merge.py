    def new_with_restriction(
        self,
        entities: Optional[Collection[str]] = None,
        relations: Optional[Collection[str]] = None,
    ) -> 'TriplesFactory':
        """Make a new triples factory only keeping the given entities and relations, but keeping the ID mapping.

        :param entities:
            The entities of interest. If None, defaults to all entities.
        :param relations:
            The relations of interest. If None, defaults to all relations.

        :return:
            A new triples factory, which has only a subset of the triples containing the entities and relations of
            interest. The label-to-ID mapping is *not* modified.
        """
        if self.create_inverse_triples and relations is not None:
            logger.info(
                'Since %s already contain inverse relations, the relation filter is expanded to contain the inverse '
                'relations as well.',
                str(self),
            )
            relations = list(relations) + list(map(self.relation_to_inverse.__getitem__, relations))

        keep_mask = None

        # Filter for entities
        if entities is not None:
            keep_mask = self.get_idx_for_entities(entities=entities)
            logger.info('Keeping %d/%d entities', len(entities), self.num_entities)

        # Filter for relations
        if relations is not None:
            relation_mask = self.get_idx_for_relations(relations=relations)
            logger.info('Keeping %d/%d relations', len(relations), self.num_relations)
            keep_mask = relation_mask if keep_mask is None else keep_mask & relation_mask

        # No filtering happened
        if keep_mask is None:
            return self

        logger.info('Keeping %d/%d triples', keep_mask.sum(), self.num_triples)
        factory = TriplesFactory.from_labeled_triples(
            triples=self.triples[keep_mask],
            create_inverse_triples=False,
            entity_to_id=self.entity_to_id,
            relation_to_id=self.relation_to_id,
            compact_id=False,
        )

        # manually copy the inverse relation mappings
        if self.create_inverse_triples:
            factory.relation_to_inverse = self.relation_to_inverse

        return factory