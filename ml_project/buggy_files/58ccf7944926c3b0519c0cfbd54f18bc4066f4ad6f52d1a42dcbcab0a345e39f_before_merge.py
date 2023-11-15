    def _decay_weights_op(self, var):
        if not self._decay_var_list or var.ref() in self._decay_var_list:
            return var.assign_sub(
                self._get_hyper("weight_decay", var.dtype) * var, self._use_locking
            )
        return tf.no_op()