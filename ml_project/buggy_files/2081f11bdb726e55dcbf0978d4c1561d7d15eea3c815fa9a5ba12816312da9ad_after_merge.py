def openaigpt_tokens_cleaner(
    token_ids: List[int], token_strings: List[Text]
) -> Tuple[List[int], List[Text]]:
    """Clean up tokens with the extra delimiters(</w>) OpenAIGPT adds while breaking a
    token into sub-tokens"""
    return cleanup_tokens(list(zip(token_ids, token_strings)), "</w>")