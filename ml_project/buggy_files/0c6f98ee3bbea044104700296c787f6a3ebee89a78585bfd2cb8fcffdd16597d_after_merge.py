def build_parfor_definitions(parfor, definitions=None):
    """get variable definition table for parfors"""
    if definitions is None:
        definitions = defaultdict(list)

    # avoid wrap_parfor_blocks() since build_definitions is called inside
    # find_potential_aliases_parfor where the parfor is already wrapped
    build_definitions(parfor.loop_body, definitions)
    build_definitions({0: parfor.init_block}, definitions)
    return definitions