    def _expand_batch(self, batch_shape):
        lazy_tensors = [lazy_tensor._expand_batch(batch_shape) for lazy_tensor in self.lazy_tensors]
        res = self.__class__(*lazy_tensors, dim=self.cat_dim, output_device=self.output_device)
        return res