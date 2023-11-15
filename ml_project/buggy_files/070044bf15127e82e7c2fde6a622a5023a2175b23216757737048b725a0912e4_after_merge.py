def resolve_is_lower_case(tokenizer):
    if isinstance(tokenizer, transformers.BertTokenizer):
        return tokenizer.basic_tokenizer.do_lower_case
    if isinstance(tokenizer, transformers.AlbertTokenizer):
        return tokenizer.do_lower_case
    else:
        return False