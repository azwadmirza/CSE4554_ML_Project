def get_relations(triples) -> Set:
    """Get all relations from the triples."""
    return set(triples[:, 1])