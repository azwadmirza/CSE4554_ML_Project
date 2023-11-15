def combine_missing(a, b):
    assert a.offset == 0
    if a.null_count > 0 or b.null_count > 0:
        # not optimal
        nulls = pc.invert(pc.or_(a.is_null(), b.is_null()))
        assert nulls.offset == 0
        nulls_buffer = nulls.buffers()[1]
        # this is not the case: no reason why it should be (TODO: open arrow issue)
        # assert nulls.buffers()[0] is None
    else:
        nulls_buffer = None
    buffers = a.buffers()
    return pa.Array.from_buffers(a.type, len(a), [nulls_buffer] + buffers[1:])