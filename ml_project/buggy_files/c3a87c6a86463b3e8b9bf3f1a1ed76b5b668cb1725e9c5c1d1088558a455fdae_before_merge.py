def gpt2_tokens_cleaner(token_strings: List[Text]) -> List[Text]:
    """Clean up tokens with the extra delimiters(</w>) GPT2 adds while breaking a token
    into sub-tokens"""
    tokens = [string.replace("Ġ", "") for string in token_strings]
    return [string for string in tokens if string]