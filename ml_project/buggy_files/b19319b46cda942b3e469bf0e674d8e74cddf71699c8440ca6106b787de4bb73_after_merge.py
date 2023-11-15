def reindex(*triples_factories: TriplesFactory) -> List[TriplesFactory]:
    """Reindex a set of triples factories."""
    # get entities and relations occurring in triples
    all_triples = torch.cat([
        factory.mapped_triples
        for factory in triples_factories
    ], dim=0)

    # generate ID translation and new label to Id mappings
    one_factory = triples_factories[0]
    (entity_to_id, entity_id_translation), (relation_to_id, relation_id_translation) = [
        _generate_compact_vectorized_lookup(
            ids=all_triples[:, cols],
            label_to_id=label_to_id,
        )
        for cols, label_to_id in (
            ([0, 2], one_factory.entity_to_id),
            (1, one_factory.relation_to_id),
        )
    ]

    return [
        TriplesFactory(
            entity_to_id=entity_to_id,
            relation_to_id=relation_to_id,
            mapped_triples=_translate_triples(
                triples=factory.mapped_triples,
                entity_translation=entity_id_translation,
                relation_translation=relation_id_translation,
            ),
            create_inverse_triples=factory.create_inverse_triples,
        )
        for factory in triples_factories
    ]