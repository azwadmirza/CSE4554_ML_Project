def resolve_is_lower_case(tokenizer):
    if isinstance(tokenizer, (transformers.BertTokenizer, transformers.AlbertTokenizer)):
        return tokenizer.basic_tokenizer.do_lower_case
    else:
        return False