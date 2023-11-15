    def new_tensors(self, inputs, shape, dtype=None, chunks=None, nsplits=None,
                    output_limit=None, kws=None, **kw):
        tensor_cls = SparseTensor if getattr(self, 'issparse')() else Tensor
        output_limit = getattr(self, 'output_limit') if output_limit is None else output_limit

        self.check_inputs(inputs)
        getattr(self, '_set_inputs')(inputs)
        if getattr(self, '_key', None) is None:
            getattr(self, 'update_key')()  # update key when inputs are set

        if isinstance(shape, (list, tuple)) and len(shape) > 0 and isinstance(shape[0], (list, tuple)):
            if not np.isinf(output_limit) and len(shape) != output_limit:
                raise ValueError('shape size must be equal to output limit, expect {0}, got {1}'.format(
                    output_limit, len(shape)))
        else:
            shape = [shape] * output_limit

        if kws is not None and kw:
            raise ValueError('can only pass kws or kw')

        tensors = []
        raw_chunks = chunks
        raw_nsplits = nsplits
        for i, s in enumerate(shape):
            dt = None
            if kws:
                kw = kws[i]
                chunks = kw.pop('chunks', raw_chunks)
                nsplits = kw.pop('nsplits', raw_nsplits)
                dt = kw.pop('dtype', None)
            if nsplits is not None:
                kw['_nsplits'] = nsplits
            if dt is None:
                dt = dtype[i] if isinstance(dtype, (tuple, list)) else dtype
            data = TensorData(_shape=s, _dtype=dt, _op=self,
                              _chunks=chunks, **kw)
            tensors.append(tensor_cls(data))

        setattr(self, 'outputs', tensors)
        if len(tensors) > 1:
            # for each output tensor, hold the reference to the other outputs
            # so that either no one or everyone are gc collected
            for i, t in enumerate(tensors):
                t.data._siblings = [tensor.data for tensor in tensors[:i] + tensors[i+1:]]
        return tensors