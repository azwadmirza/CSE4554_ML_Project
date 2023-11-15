    def gradients(self, optimizer, loss):
        if self.config["grad_norm_clipping"] is not None:
            self.gvs = {
                k: minimize_and_clip(optimizer, self.losses[k], self.vars[k],
                                     self.config["grad_norm_clipping"])
                for k, optimizer in self.optimizers.items()
            }
        else:
            self.gvs = {
                k: optimizer.compute_gradients(self.losses[k], self.vars[k])
                for k, optimizer in self.optimizers.items()
            }
        return self.gvs["critic"] + self.gvs["actor"]