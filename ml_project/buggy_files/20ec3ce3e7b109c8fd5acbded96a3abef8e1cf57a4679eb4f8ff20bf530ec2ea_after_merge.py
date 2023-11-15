def _prepare_cleanup(
    training: MappedTriples,
    testing: MappedTriples,
    max_ids: Optional[Tuple[int, int]] = None,
) -> torch.BoolTensor:
    """
    Calculate a mask for the test triples with triples containing test-only entities or relations.

    :param training: shape: (n, 3)
        The training triples.
    :param testing: shape: (m, 3)
        The testing triples.

    :return: shape: (m,)
        The move mask.
    """
    # base cases
    if len(testing) == 0:
        return torch.empty(0, dtype=torch.bool)
    if len(training) == 0:
        return torch.ones(testing.shape[0], dtype=torch.bool)

    columns = [[0, 2], [1]]
    to_move_mask = torch.zeros(1, dtype=torch.bool)
    if max_ids is None:
        max_ids = [
            max(training[:, col].max().item(), testing[:, col].max().item()) + 1
            for col in columns
        ]
    for col, max_id in zip(columns, max_ids):
        # IDs not in training
        not_in_training_mask = torch.ones(max_id, dtype=torch.bool)
        not_in_training_mask[training[:, col].view(-1)] = False

        # triples with exclusive test IDs
        exclusive_triples = not_in_training_mask[testing[:, col].view(-1)].view(-1, len(col)).any(dim=-1)
        to_move_mask = to_move_mask | exclusive_triples
    return to_move_mask