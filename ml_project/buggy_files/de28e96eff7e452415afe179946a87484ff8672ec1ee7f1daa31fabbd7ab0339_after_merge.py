def get_relations(triples: torch.LongTensor) -> Set[int]:
    """Get all relations from the triples."""
    return set(triples[:, 1].tolist())