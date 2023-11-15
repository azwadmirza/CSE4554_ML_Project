def _is_token_non_standard(symbol: str, address: ChecksumEthAddress) -> bool:
    """ignore some assets we do not query directly as token balances"""
    if symbol in ('UNI-V2',):
        return True

    if address in ('0xCb2286d9471cc185281c4f763d34A962ED212962',):  # Sushi LP token
        return True

    return False