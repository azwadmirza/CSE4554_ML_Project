def get_copies_parfor(parfor, typemap):
    """find copies generated/killed by parfor"""
    blocks = wrap_parfor_blocks(parfor)
    in_copies_parfor, out_copies_parfor = copy_propagate(blocks, typemap)
    in_gen_copies, in_extra_kill = get_block_copies(blocks, typemap)
    unwrap_parfor_blocks(parfor)

    # parfor's extra kill is all possible gens and kills of it's loop
    kill_set = in_extra_kill[0]
    for label in parfor.loop_body.keys():
        kill_set |= { l for l,r in in_gen_copies[label] }
    last_label = max(parfor.loop_body.keys())
    if config.DEBUG_ARRAY_OPT==1:
        print("copy propagate parfor out_copies:",
            out_copies_parfor[last_label], "kill_set",kill_set)
    return out_copies_parfor[last_label], kill_set