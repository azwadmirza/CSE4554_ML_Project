def get_tokenizer(model_name: str, **kwargs) -> transformers.PreTrainedTokenizer:
    cache_key = (model_name, frozenset(kwargs.items()))

    global _tokenizer_cache
    tokenizer = _tokenizer_cache.get(cache_key, None)
    if tokenizer is None:
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            model_name,
            **kwargs,
        )
        _tokenizer_cache[cache_key] = tokenizer
    return tokenizer