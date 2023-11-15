def get_entities(triples: torch.LongTensor) -> Set[int]:
    """Get all entities from the triples."""
    return set(triples[:, [0, 2]].flatten().tolist())