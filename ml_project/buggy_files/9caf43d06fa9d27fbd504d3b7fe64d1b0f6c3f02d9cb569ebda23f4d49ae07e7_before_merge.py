def _proc_as_batch(proc, x, axis):
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