def get_parfor_call_table(parfor, call_table={}, reverse_call_table={}):
    blocks = wrap_parfor_blocks(parfor)
    call_table, reverse_call_table = get_call_table(blocks, call_table,
        reverse_call_table)
    unwrap_parfor_blocks(parfor)
    return call_table, reverse_call_table