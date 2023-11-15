    def from_labeled_triples(
        cls,
        triples: LabeledTriples,
        create_inverse_triples: bool = False,
        entity_to_id: Optional[EntityMapping] = None,
        relation_to_id: Optional[RelationMapping] = None,
        compact_id: bool = True,
    ) -> 'TriplesFactory':
        """
        Create a new triples factory from label-based triples.

        :param triples: shape: (n, 3), dtype: str
            The label-based triples.
        :param create_inverse_triples:
            Whether to create inverse triples.
        :param entity_to_id:
            The mapping from entity labels to ID. If None, create a new one from the triples.
        :param relation_to_id:
            The mapping from relations labels to ID. If None, create a new one from the triples.
        :param compact_id:
            Whether to compact IDs such that the IDs are consecutive.

        :return:
            A new triples factory.
        """
        relations = triples[:, 1]
        unique_relations = set(relations)

        # Check if the triples are inverted already
        relations_already_inverted = cls._check_already_inverted_relations(unique_relations)

        # TODO: invert triples id-based
        if create_inverse_triples or relations_already_inverted:
            create_inverse_triples = True
            if relations_already_inverted:
                logger.info(
                    f'Some triples already have suffix {INVERSE_SUFFIX}. '
                    f'Creating TriplesFactory based on inverse triples',
                )
                relation_to_inverse = {
                    re.sub('_inverse$', '', relation): f"{re.sub('_inverse$', '', relation)}{INVERSE_SUFFIX}"
                    for relation in unique_relations
                }

            else:
                relation_to_inverse = {
                    relation: f"{relation}{INVERSE_SUFFIX}"
                    for relation in unique_relations
                }
                inverse_triples = np.stack(
                    [
                        triples[:, 2],
                        np.array([relation_to_inverse[relation] for relation in relations], dtype=np.str),
                        triples[:, 0],
                    ],
                    axis=-1,
                )
                # extend original triples with inverse ones
                triples = np.concatenate([triples, inverse_triples], axis=0)

        else:
            create_inverse_triples = False
            relation_to_inverse = None

        # Generate entity mapping if necessary
        if entity_to_id is None:
            entity_to_id = create_entity_mapping(triples=triples)
        if compact_id:
            entity_to_id = compact_mapping(mapping=entity_to_id)[0]

        # Generate relation mapping if necessary
        if relation_to_id is None:
            if create_inverse_triples:
                relation_to_id = create_relation_mapping(
                    set(relation_to_inverse.keys()).union(set(relation_to_inverse.values())),
                )
            else:
                relation_to_id = create_relation_mapping(unique_relations)
        if compact_id:
            relation_to_id = compact_mapping(mapping=relation_to_id)[0]

        # Map triples of labels to triples of IDs.
        mapped_triples = _map_triples_elements_to_ids(
            triples=triples,
            entity_to_id=entity_to_id,
            relation_to_id=relation_to_id,
        )

        return cls(
            entity_to_id=entity_to_id,
            relation_to_id=relation_to_id,
            _triples=triples,
            mapped_triples=mapped_triples,
            relation_to_inverse=relation_to_inverse,
        )