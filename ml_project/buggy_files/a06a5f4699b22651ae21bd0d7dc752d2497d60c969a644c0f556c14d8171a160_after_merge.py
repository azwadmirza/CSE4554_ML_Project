def _tf_cleanup_randomized(
    training: MappedTriples,
    testing: MappedTriples,
    random_state: TorchRandomHint = None,
) -> Tuple[MappedTriples, MappedTriples]:
    """Cleanup a triples array, but randomly select testing triples and recalculate to minimize moves.

    1. Calculate ``move_id_mask`` as in :func:`_tf_cleanup_deterministic`
    2. Choose a triple to move, recalculate move_id_mask
    3. Continue until move_id_mask has no true bits
    """
    generator = ensure_torch_random_state(random_state)
    move_id_mask = _prepare_cleanup(training, testing)

    # While there are still triples that should be moved to the training set
    while move_id_mask.any():
        # Pick a random triple to move over to the training triples
        candidates, = move_id_mask.nonzero(as_tuple=True)
        idx = torch.randint(candidates.shape[0], size=(1,), generator=generator)
        idx = candidates[idx]

        # add to training
        training = torch.cat([training, testing[idx].view(1, -1)], dim=0)
        # remove from testing
        testing = torch.cat([testing[:idx], testing[idx + 1:]], dim=0)
        # Recalculate the move_id_mask
        move_id_mask = _prepare_cleanup(training, testing)

    return training, testing