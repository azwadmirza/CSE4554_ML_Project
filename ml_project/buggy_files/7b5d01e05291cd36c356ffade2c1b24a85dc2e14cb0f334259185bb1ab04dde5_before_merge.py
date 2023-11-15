    def tile(cls, op: "LGBMAlign"):
        inputs = [d for d in [op.data, op.label, op.sample_weight, op.init_score] if d is not None]
        data = op.data

        ctx = get_context()
        if ctx.running_mode != RunningMode.distributed:
            outputs = [inp.rechunk(tuple((s,) for s in inp.shape))._inplace_tile() for inp in inputs]
        else:
            if len(data.nsplits[1]) != 1:
                data = data.rechunk({1: data.shape[1]})._inplace_tile()
            outputs = [data]
            for inp in inputs[1:]:
                if inp is not None:
                    outputs.append(inp.rechunk((data.nsplits[0],))._inplace_tile())

        kws = []
        for o in outputs:
            kw = o.params.copy()
            kw.update(dict(chunks=o.chunks, nsplits=o.nsplits))
            kws.append(kw)

        new_op = op.copy().reset_key()
        tileables = new_op.new_tileables(inputs, kws=kws)

        return tileables