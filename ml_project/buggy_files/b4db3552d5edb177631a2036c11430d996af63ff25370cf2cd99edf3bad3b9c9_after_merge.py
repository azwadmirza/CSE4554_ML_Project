    def apply_gradients(self, grads_and_vars, name=None):
        bin_grads_and_vars, fp_grads_and_vars = [], []
        for grad, var in grads_and_vars:
            if self.is_binary(var):
                bin_grads_and_vars.append((grad, var))
            else:
                fp_grads_and_vars.append((grad, var))

        bin_train_op = super().apply_gradients(bin_grads_and_vars, name=name)

        fp_train_op = self.fp_optimizer.apply_gradients(fp_grads_and_vars, name=name)
        return tf.group(bin_train_op, fp_train_op, name="train_with_bop")