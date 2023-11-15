def generate_triples_factory(
    num_entities: int = 33,
    num_relations: int = 7,
    num_triples: int = 101,
    random_state: TorchRandomHint = None,
    create_inverse_triples: bool = False,
) -> TriplesFactory:
    """Generate a triples factory with random triples."""
    mapped_triples = generate_triples(
        num_entities=num_entities,
        num_relations=num_relations,
        num_triples=num_triples,
        random_state=random_state,
    )
    return TriplesFactory(
        entity_to_id=_make_label_to_ids(num_entities),
        relation_to_id=_make_label_to_ids(num_relations),
        mapped_triples=mapped_triples,
        create_inverse_triples=create_inverse_triples,
    )