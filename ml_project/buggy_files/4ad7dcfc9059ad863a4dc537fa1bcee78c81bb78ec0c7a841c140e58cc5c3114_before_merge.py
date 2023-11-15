    def run_batch_backward_pass(self, split_batch, batch_idx, opt_idx, optimizer):
        # ------------------
        # GRAD NORMS
        # ------------------
        # track gradient norms when requested
        grad_norm_dic = {}
        if batch_idx % self.row_log_interval == 0:
            if float(self.track_grad_norm) > 0:
                model = self.get_model()
                grad_norm_dic = model.grad_norm(
                    self.track_grad_norm)

        # ------------------
        # CLIP GRADS
        # ------------------
        if self.use_amp and NATIVE_AMP_AVALAIBLE:
            self.scaler.unscale_(optimizer)
        self.clip_gradients()

        # ------------------
        # .STEP + ZERO_GRAD
        # ------------------
        self.call_optimizer_step(optimizer, opt_idx, batch_idx, split_batch)

        return grad_norm_dic