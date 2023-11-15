def generate_triples_factory(
    num_entities: int = 33,
    num_relations: int = 7,
    num_triples: int = 101,
    random_state: RandomHint = None,
    create_inverse_triples: bool = False,
) -> TriplesFactory:
    """Generate a triples factory with random triples."""
    triples = generate_labeled_triples(
        num_entities=num_entities,
        num_relations=num_relations,
        num_triples=num_triples,
        random_state=random_state,
    )
    return TriplesFactory.from_labeled_triples(
        triples=triples,
        create_inverse_triples=create_inverse_triples,
    )