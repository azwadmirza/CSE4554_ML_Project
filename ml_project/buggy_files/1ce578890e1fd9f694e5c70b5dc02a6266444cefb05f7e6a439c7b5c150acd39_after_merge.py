def combine_missing(a, b):
    # return a copy of a with missing values of a and b combined
    if a.null_count > 0 or b.null_count > 0:
        a, b = vaex.arrow.convert.align(a, b)
        if isinstance(a, pa.ChunkedArray):
            # divide and conquer
            assert isinstance(b, pa.ChunkedArray)
            assert len(a.chunks) == len(b.chunks)
            return pa.chunked_array([combine_missing(ca, cb) for ca, cb in zip(a.chunks, b.chunks)])
        if a.offset != 0:
            a = vaex.arrow.convert.trim_buffers_ipc(a)
        if b.offset != 0:
            b = vaex.arrow.convert.trim_buffers_ipc(b)
        assert a.offset == 0
        assert b.offset == 0
        # not optimal
        nulls = pc.invert(pc.or_(a.is_null(), b.is_null()))
        assert nulls.offset == 0
        nulls_buffer = nulls.buffers()[1]
        # this is not the case: no reason why it should be (TODO: open arrow issue)
        # assert nulls.buffers()[0] is None
        buffers = a.buffers()
        return pa.Array.from_buffers(a.type, len(a), [nulls_buffer] + buffers[1:])
    else:
        return a