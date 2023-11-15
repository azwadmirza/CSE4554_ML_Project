def get_entities(triples) -> Set:
    """Get all entities from the triples."""
    return set(triples[:, [0, 2]].flatten().tolist())