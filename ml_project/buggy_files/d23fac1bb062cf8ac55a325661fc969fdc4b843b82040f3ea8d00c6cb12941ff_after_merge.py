    def fetch_tensors(self, tensors, **kw):
        from .tensor.expressions.fetch import TensorFetch

        results = []
        to_concat_tensors = OrderedDict()

        for i, tensor in enumerate(tensors):
            if tensor.key not in self.stored_tensors:
                # check if the tensor is executed before
                raise ValueError(
                    'Tensor to fetch must be executed before, got {0}'.format(tensor))

            if len(tensor.chunks) == 1:
                result = self._chunk_result[tensor.chunks[0].key]
                results.append(result)
                continue

            # generate TensorFetch op for each chunk
            chunks = []
            for c in tensor.chunks:
                op = TensorFetch(dtype=c.dtype, sparse=c.op.sparse)
                chunk = op.new_chunk(None, c.shape, index=c.index, _key=c.key)
                chunks.append(chunk)

            new_op = TensorFetch(dtype=tensor.dtype, sparse=tensor.op.sparse)
            # copy key and id to ensure that fetch tensor won't add the count of executed tensor
            tensor = new_op.new_tensor(None, tensor.shape, chunks=chunks,
                                       nsplits=tensor.nsplits, _key=tensor.key, _id=tensor.id)

            # add this concat tensor into the list which shall be executed later
            to_concat_tensors[i] = tensor
            results.append(None)

        # execute the concat tensors together
        if to_concat_tensors:
            concat_results = self.execute_tensors(list(to_concat_tensors.values()), **kw)
            for j, concat_result in zip(to_concat_tensors, concat_results):
                results[j] = concat_result

        return results