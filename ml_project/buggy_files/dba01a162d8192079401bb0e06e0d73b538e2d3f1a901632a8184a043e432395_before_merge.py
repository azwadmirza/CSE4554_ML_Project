def generate_labeled_triples(
    num_entities: int = 33,
    num_relations: int = 7,
    num_triples: int = 101,
    random_state: RandomHint = None,
) -> np.ndarray:
    """Generate labeled random triples."""
    t = generate_triples(
        num_entities=num_entities,
        num_relations=num_relations,
        num_triples=num_triples,
        compact=False,
        random_state=random_state,
    )
    entity_id_to_label = _make_id_to_labels(num_entities)
    relation_id_to_label = _make_id_to_labels(num_relations)
    return np.asarray([
        (
            entity_id_to_label[h],
            relation_id_to_label[r],
            entity_id_to_label[t],
        )
        for h, r, t in t
    ], dtype=str)