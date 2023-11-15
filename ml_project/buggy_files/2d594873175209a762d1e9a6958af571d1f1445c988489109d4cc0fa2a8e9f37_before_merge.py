def _prepare_cleanup(training: np.ndarray, testing: np.ndarray):
    training_entities = _get_unique(training)
    testing_entities = _get_unique(testing)
    to_move = testing_entities[~np.isin(testing_entities, training_entities)]
    move_id_mask = np.isin(testing[:, [0, 2]], to_move).any(axis=1)
    return training_entities, testing_entities, to_move, move_id_mask