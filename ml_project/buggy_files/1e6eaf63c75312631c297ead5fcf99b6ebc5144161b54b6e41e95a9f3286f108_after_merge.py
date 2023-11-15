def try_fuse(parfor1, parfor2):
    """try to fuse parfors and return a fused parfor, otherwise return None
    """
    dprint("try_fuse trying to fuse \n", parfor1, "\n", parfor2)

    # fusion of parfors with different dimensions not supported yet
    if len(parfor1.loop_nests) != len(parfor2.loop_nests):
        dprint("try_fuse parfors number of dimensions mismatch")
        return None

    ndims = len(parfor1.loop_nests)
    # all loops should be equal length
    for i in range(ndims):
        if parfor1.loop_nests[i].correlation != parfor2.loop_nests[i].correlation:
            dprint("try_fuse parfor dimension correlation mismatch", i)
            return None

    # TODO: make sure parfor1's reduction output is not used in parfor2
    # only data parallel loops
    if has_cross_iter_dep(parfor1) or has_cross_iter_dep(parfor2):
        dprint("try_fuse parfor cross iteration dependency found")
        return None

    # make sure parfor2's init block isn't using any output of parfor1
    parfor1_body_usedefs = compute_use_defs(parfor1.loop_body)
    parfor1_body_vardefs = set()
    for defs in parfor1_body_usedefs.defmap.values():
        parfor1_body_vardefs |= defs
    init2_uses = compute_use_defs({0: parfor2.init_block}).usemap[0]
    if not parfor1_body_vardefs.isdisjoint(init2_uses):
        dprint("try_fuse parfor2 init block depends on parfor1 body")
        return None

    return fuse_parfors_inner(parfor1, parfor2)