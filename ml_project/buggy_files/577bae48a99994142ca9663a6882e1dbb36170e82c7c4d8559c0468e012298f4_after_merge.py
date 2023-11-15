    def apply_gradients(self, grads_and_vars, name: Optional[str] = None, **kwargs):
        """Apply gradients to variables for each optimizer.

        On the first call to `apply_gradients()`, compute the mapping from variables to
        optimizers and cache it in the `self.var_opt_mapping` dict for serialization and
        faster access.
        """

        if self.var_opt_mapping is None:
            # Convert `grads_and_vars` to list so we can iterate multiple times over it
            grads_and_vars = list(grads_and_vars)
            self._compute_var_opt_mapping(grads_and_vars)

        # Split gradients and variables into a separate list for each optimizer
        grad_var_lists = [[] for _ in range(len(self.pred_opt_pairs) + 1)]
        for grad, var in grads_and_vars:
            if var.name in self.var_opt_mapping:
                grad_var_lists[self.var_opt_mapping[var.name]].append((grad, var))

        with tf.init_scope():
            for optimizer, opt_grads_and_vars in zip(self.optimizers, grad_var_lists):
                optimizer._create_slots([v for (_, v) in grads_and_vars])

        return tf.distribute.get_replica_context().merge_call(
            self._apply_gradients, args=(grad_var_lists, name), kwargs=kwargs
        )