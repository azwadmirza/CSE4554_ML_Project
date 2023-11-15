def get_parfor_tuple_table(parfor, tuple_table={}):
    blocks = wrap_parfor_blocks(parfor)
    tuple_table = ir_utils.get_tuple_table(blocks, tuple_table)
    unwrap_parfor_blocks(parfor)
    return tuple_table