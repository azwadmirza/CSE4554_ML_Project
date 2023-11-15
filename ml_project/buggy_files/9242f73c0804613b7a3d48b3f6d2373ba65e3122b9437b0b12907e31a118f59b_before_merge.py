def get_parfor_params_inner(parfor, pre_defs, options_fusion, fusion_info):

    blocks = wrap_parfor_blocks(parfor)
    cfg = compute_cfg_from_blocks(blocks)
    usedefs = compute_use_defs(blocks)
    live_map = compute_live_map(cfg, blocks, usedefs.usemap, usedefs.defmap)
    parfor_ids = get_parfor_params(blocks, options_fusion, fusion_info)
    n_parfors = len(parfor_ids)
    if n_parfors > 0:
        if config.DEBUG_ARRAY_OPT_STATS:
            after_fusion = ("After fusion" if options_fusion
                            else "With fusion disabled")
            print(('{}, parallel for-loop {} has '
                'nested Parfor(s) #{}.').format(
                after_fusion, parfor.id, n_parfors, parfor_ids))
        fusion_info[parfor.id] = list(parfor_ids)

    unwrap_parfor_blocks(parfor)
    keylist = sorted(live_map.keys())
    init_block = keylist[0]
    first_non_init_block = keylist[1]

    before_defs = usedefs.defmap[init_block] | pre_defs
    params = live_map[first_non_init_block] & before_defs
    return params