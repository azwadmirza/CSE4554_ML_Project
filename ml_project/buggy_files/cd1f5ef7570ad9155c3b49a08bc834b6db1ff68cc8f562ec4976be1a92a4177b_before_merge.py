def add_sentence_boundary_token_ids(
    tensor: torch.Tensor, mask: torch.BoolTensor, sentence_begin_token: Any, sentence_end_token: Any
) -> Tuple[torch.Tensor, torch.BoolTensor]:
    """
    Add begin/end of sentence tokens to the batch of sentences.
    Given a batch of sentences with size `(batch_size, timesteps)` or
    `(batch_size, timesteps, dim)` this returns a tensor of shape
    `(batch_size, timesteps + 2)` or `(batch_size, timesteps + 2, dim)` respectively.

    Returns both the new tensor and updated mask.

    # Parameters

    tensor : `torch.Tensor`
        A tensor of shape `(batch_size, timesteps)` or `(batch_size, timesteps, dim)`
    mask : `torch.BoolTensor`
         A tensor of shape `(batch_size, timesteps)`
    sentence_begin_token: `Any`
        Can be anything that can be broadcast in torch for assignment.
        For 2D input, a scalar with the `<S>` id. For 3D input, a tensor with length dim.
    sentence_end_token: `Any`
        Can be anything that can be broadcast in torch for assignment.
        For 2D input, a scalar with the `</S>` id. For 3D input, a tensor with length dim.

    # Returns

    tensor_with_boundary_tokens : `torch.Tensor`
        The tensor with the appended and prepended boundary tokens. If the input was 2D,
        it has shape (batch_size, timesteps + 2) and if the input was 3D, it has shape
        (batch_size, timesteps + 2, dim).
    new_mask : `torch.BoolTensor`
        The new mask for the tensor, taking into account the appended tokens
        marking the beginning and end of the sentence.
    """
    # TODO: matthewp, profile this transfer
    sequence_lengths = mask.sum(dim=1).detach().cpu().numpy()
    tensor_shape = list(tensor.data.shape)
    new_shape = list(tensor_shape)
    new_shape[1] = tensor_shape[1] + 2
    tensor_with_boundary_tokens = tensor.new_zeros(*new_shape)
    if len(tensor_shape) == 2:
        tensor_with_boundary_tokens[:, 1:-1] = tensor
        tensor_with_boundary_tokens[:, 0] = sentence_begin_token
        for i, j in enumerate(sequence_lengths):
            tensor_with_boundary_tokens[i, j + 1] = sentence_end_token
        new_mask = tensor_with_boundary_tokens != 0
    elif len(tensor_shape) == 3:
        tensor_with_boundary_tokens[:, 1:-1, :] = tensor
        for i, j in enumerate(sequence_lengths):
            tensor_with_boundary_tokens[i, 0, :] = sentence_begin_token
            tensor_with_boundary_tokens[i, j + 1, :] = sentence_end_token
        new_mask = (tensor_with_boundary_tokens > 0).sum(dim=-1) > 0
    else:
        raise ValueError("add_sentence_boundary_token_ids only accepts 2D and 3D input")

    return tensor_with_boundary_tokens, new_mask