def openaigpt_tokens_cleaner(token_strings: List[Text]) -> List[Text]:
    """Clean up tokens with the extra delimiters(</w>) OpenAIGPT adds while breaking a
    token into sub-tokens"""
    tokens = [string.replace("</w>", "") for string in token_strings]
    return [string for string in tokens if string]