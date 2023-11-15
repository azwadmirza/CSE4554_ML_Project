def find_potential_aliases_parfor(parfor, args, typemap, alias_map, arg_aliases):
    blocks = wrap_parfor_blocks(parfor)
    ir_utils.find_potential_aliases(
        blocks, args, typemap, alias_map, arg_aliases)
    unwrap_parfor_blocks(parfor)
    return