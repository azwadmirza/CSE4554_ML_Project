def reindex(*triples_factories: TriplesFactory) -> List[TriplesFactory]:
    """Reindex a set of triples factories."""
    triples = np.concatenate(
        [
            triples_factory.triples
            for triples_factory in triples_factories
        ],
        axis=0,
    )
    entity_to_id = create_entity_mapping(triples)
    relation_to_id = create_relation_mapping(set(triples[:, 1]))

    return [
        TriplesFactory.from_labeled_triples(
            triples=triples_factory.triples,
            entity_to_id=entity_to_id,
            relation_to_id=relation_to_id,
            # FIXME doesn't carry flag of create_inverse_triples through
        )
        for triples_factory in triples_factories
    ]