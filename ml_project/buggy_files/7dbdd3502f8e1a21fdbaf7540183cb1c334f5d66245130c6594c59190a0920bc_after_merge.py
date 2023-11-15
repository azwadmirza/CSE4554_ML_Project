    def _new_entities(self, inputs, shape, chunks=None, nsplits=None, output_limit=None,
                      kws=None, **kw):
        output_limit = getattr(self, 'output_limit') if output_limit is None else output_limit

        self.check_inputs(inputs)
        getattr(self, '_set_inputs')(inputs)
        if getattr(self, '_key', None) is None:
            getattr(self, '_update_key')()  # update key when inputs are set

        if isinstance(shape, (list, tuple)) and len(shape) > 0 and isinstance(shape[0], (list, tuple)):
            if not np.isinf(output_limit) and len(shape) != output_limit:
                raise ValueError('shape size must be equal to output limit, expect {0}, got {1}'.format(
                    output_limit, len(shape)))
        else:
            shape = [shape] * output_limit

        entities = []
        raw_chunks = chunks
        raw_nsplits = nsplits
        for j, s in enumerate(shape):
            create_tensor_kw = kw.copy()
            if kws:
                create_tensor_kw.update(kws[j])
            chunks = create_tensor_kw.pop('chunks', raw_chunks)
            nsplits = create_tensor_kw.pop('nsplits', raw_nsplits)
            entity = self._create_entity(j, s, nsplits, chunks, **create_tensor_kw)
            entities.append(entity)

        setattr(self, 'outputs', entities)
        if len(entities) > 1:
            # for each output tensor, hold the reference to the other outputs
            # so that either no one or everyone are gc collected
            for j, t in enumerate(entities):
                t.data._siblings = [tensor.data for tensor in entities[:j] + entities[j+1:]]
        return entities