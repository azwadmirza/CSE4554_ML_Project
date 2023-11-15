    def gradients(self, optimizer, loss):
        self.gvs = {
            k: minimize_and_clip(optimizer, self.losses[k], self.vars[k],
                                 self.config["grad_norm_clipping"])
            for k, optimizer in self.optimizers.items()
        }
        return self.gvs["critic"] + self.gvs["actor"]