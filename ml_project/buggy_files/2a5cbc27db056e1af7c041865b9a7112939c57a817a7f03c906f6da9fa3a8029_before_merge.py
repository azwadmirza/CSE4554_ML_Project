def get_perplexity(loss, round=2, base=2):
    if loss is None:
        return 0.
    return safe_round(base**loss, round)