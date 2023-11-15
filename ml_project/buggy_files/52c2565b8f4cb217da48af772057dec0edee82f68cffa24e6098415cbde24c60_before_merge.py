    def _new_chunks(self, inputs, shape, index=None, output_limit=None, kws=None, **kw):
        output_limit = getattr(self, 'output_limit') if output_limit is None else output_limit

        self.check_inputs(inputs)
        getattr(self, '_set_inputs')(inputs)
        if getattr(self, '_key', None) is None:
            getattr(self, 'update_key')()  # update key when inputs are set

        if isinstance(shape, (list, tuple)) and len(shape) > 0 and isinstance(shape[0], (list, tuple)):
            if len(shape) != output_limit:
                raise ValueError('shape size must be equal to output limit, expect {0}, got {1}'.format(
                    output_limit, len(shape)))
        else:
            shape = [shape] * output_limit

        chunks = []
        raw_index = index
        for j, s in enumerate(shape):
            create_chunk_kw = kw.copy()
            if kws:
                create_chunk_kw.update(kws[j])
            index = create_chunk_kw.pop('index', raw_index)
            chunk = self._create_chunk(j, index, s, **create_chunk_kw)
            chunks.append(chunk)

        setattr(self, 'outputs', chunks)
        return chunks