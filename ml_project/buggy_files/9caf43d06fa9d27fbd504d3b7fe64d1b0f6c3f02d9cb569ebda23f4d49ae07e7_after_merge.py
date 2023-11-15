def _proc_as_batch(proc, x, axis):
    if x.shape[axis] == 0:
        return cupy.empty_like(x)
    trans, revert = _axis_to_first(x, axis)
    t = x.transpose(trans)
    s = t.shape
    r = t.reshape(x.shape[axis], -1)
    pos = 1
    size = r.size
    batch = r.shape[1]
    while pos < size:
        proc(pos, batch, r, size=size)
        pos <<= 1
    return r.reshape(s).transpose(revert)