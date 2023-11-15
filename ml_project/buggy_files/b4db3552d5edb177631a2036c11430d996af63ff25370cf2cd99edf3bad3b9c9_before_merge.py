    def apply_gradients(self, grads_and_vars, name=None):
        bin_grads_and_vars = [(g, v) for g, v in grads_and_vars if self.is_binary(v)]
        fp_grads_and_vars = [(g, v) for g, v in grads_and_vars if not self.is_binary(v)]

        bin_train_op = super().apply_gradients(bin_grads_and_vars, name=name)
        fp_train_op = self.fp_optimizer.apply_gradients(fp_grads_and_vars, name=name)

        return tf.group(bin_train_op, fp_train_op, name="train_with_bop")