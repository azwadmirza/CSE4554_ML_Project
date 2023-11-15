def enforce_max_size(token_embedding, size):
    assert token_embedding.idx_to_vec is not None
    if size and len(token_embedding.idx_to_token) > size:
        assert size > 0
        size = size + 1 if token_embedding.unknown_token is not None else size
        token_embedding._idx_to_token = token_embedding._idx_to_token[:size]
        token_embedding._idx_to_vec = token_embedding._idx_to_vec[:size]
        token_embedding._token_to_idx = {
            token: idx
            for idx, token in enumerate(token_embedding._idx_to_token)
        }