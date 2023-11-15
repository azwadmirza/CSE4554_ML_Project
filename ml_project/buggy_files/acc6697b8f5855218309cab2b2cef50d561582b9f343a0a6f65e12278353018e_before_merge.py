def _slice_as_ndarray(strace, idx):
    if idx.start is None:
        burn = 0
    else:
        burn = idx.start
    if idx.step is None:
        thin = 1
    else:
        thin = idx.step

    sliced = NDArray(model=strace.model, vars=strace.vars)
    sliced.chain = strace.chain
    sliced.samples = {v: strace.get_values(v, burn=burn, thin=thin)
                      for v in strace.varnames}
    return sliced