def build_parfor_definitions(parfor, definitions=None):
    """get variable definition table for parfors"""
    if definitions is None:
        definitions = dict()

    blocks = wrap_parfor_blocks(parfor)
    build_definitions(blocks, definitions)
    unwrap_parfor_blocks(parfor)
    return definitions