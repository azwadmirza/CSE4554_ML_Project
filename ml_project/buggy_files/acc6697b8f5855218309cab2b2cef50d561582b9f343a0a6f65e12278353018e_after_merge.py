def _slice_as_ndarray(strace, idx):
    sliced = NDArray(model=strace.model, vars=strace.vars)
    sliced.chain = strace.chain

    # Happy path where we do not need to load everything from the trace
    if ((idx.step is None or idx.step >= 1) and
            (idx.stop is None or idx.stop == len(strace))):
        start, stop, step = idx.indices(len(strace))
        sliced.samples = {v: strace.get_values(v, burn=idx.start, thin=idx.step)
                          for v in strace.varnames}
        sliced.draw_idx = (stop - start) // step
    else:
        start, stop, step = idx.indices(len(strace))
        sliced.samples = {v: strace.get_values(v)[start:stop:step]
                          for v in strace.varnames}
        sliced.draw_idx = (stop - start) // step

    return sliced