def generate_triples(
    num_entities: int = 33,
    num_relations: int = 7,
    num_triples: int = 101,
    compact: bool = True,
    random_state: RandomHint = None,
) -> np.ndarray:
    """Generate random triples."""
    random_state = ensure_random_state(random_state)
    rv = np.stack([
        random_state.randint(num_entities, size=(num_triples,)),
        random_state.randint(num_relations, size=(num_triples,)),
        random_state.randint(num_entities, size=(num_triples,)),
    ], axis=1)

    if compact:
        new_entity_id = {
            entity: i
            for i, entity in enumerate(sorted(get_entities(rv)))
        }
        new_relation_id = {
            relation: i
            for i, relation in enumerate(sorted(get_relations(rv)))
        }
        rv = np.asarray([
            [new_entity_id[h], new_relation_id[r], new_entity_id[t]]
            for h, r, t in rv
        ], dtype=int)

    return rv