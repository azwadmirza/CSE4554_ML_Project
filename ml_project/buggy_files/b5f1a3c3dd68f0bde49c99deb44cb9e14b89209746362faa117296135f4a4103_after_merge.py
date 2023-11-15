def _tf_cleanup_deterministic(training: MappedTriples, testing: MappedTriples) -> Tuple[MappedTriples, MappedTriples]:
    """Cleanup a triples array (testing) with respect to another (training)."""
    move_id_mask = _prepare_cleanup(training, testing)
    training = torch.cat([training, testing[move_id_mask]])
    testing = testing[~move_id_mask]
    return training, testing