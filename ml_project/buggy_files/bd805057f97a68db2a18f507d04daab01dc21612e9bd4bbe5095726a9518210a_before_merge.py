def _is_token_non_standard(symbol: str, address: ChecksumEthAddress) -> bool:
    """ignore some assets we do not yet support and don't want to spam warnings with"""
    if symbol in ('UNI-V2', 'swUSD', 'crCRV'):
        return True

    if address in ('0xCb2286d9471cc185281c4f763d34A962ED212962',):  # Sushi LP token
        return True

    return False