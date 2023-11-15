    def _decay_weights_sparse_op(self, var, indices):
        if not self._decay_var_list or var.ref() in self._decay_var_list:
            update = -self._decayed_wd(var.dtype) * tf.gather(var, indices)
            return self._resource_scatter_add(var, indices, update)
        return tf.no_op()