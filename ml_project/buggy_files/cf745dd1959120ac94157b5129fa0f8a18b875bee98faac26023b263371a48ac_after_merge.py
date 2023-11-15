def _tf_cleanup_all(
    triples_groups: List[MappedTriples],
    *,
    random_state: TorchRandomHint = None,
) -> Sequence[MappedTriples]:
    """Cleanup a list of triples array with respect to the first array."""
    reference, *others = triples_groups
    rv = []
    for other in others:
        if random_state is not None:
            reference, other = _tf_cleanup_randomized(reference, other, random_state)
        else:
            reference, other = _tf_cleanup_deterministic(reference, other)
        rv.append(other)
    # [...] is necessary for Python 3.7 compatibility
    return [reference, *rv]