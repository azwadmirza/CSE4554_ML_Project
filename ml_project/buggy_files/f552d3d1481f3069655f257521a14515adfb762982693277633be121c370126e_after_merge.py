    def _expand_batch(self, batch_shape):
        batch_dim = self.cat_dim + 2
        if batch_dim < 0:
            if batch_shape[batch_dim] != self.batch_shape[batch_dim]:
                raise RuntimeError(
                    f"Trying to expand a CatLazyTensor in dimension {self.cat_dim}, but this is the concatenated "
                    f"dimension.\nCurrent shape: {self.shape} - expanded shape: {batch_shape + self.matrix_shape}."
                )
            lazy_tensors = []
            for lazy_tensor in self.lazy_tensors:
                sub_batch_shape = list(batch_shape).copy()
                sub_batch_shape[batch_dim] = lazy_tensor.shape[self.cat_dim]
                lazy_tensors.append(lazy_tensor._expand_batch(sub_batch_shape))
        else:
            lazy_tensors = [lazy_tensor._expand_batch(batch_shape) for lazy_tensor in self.lazy_tensors]
        res = self.__class__(*lazy_tensors, dim=self.cat_dim, output_device=self.output_device)
        return res