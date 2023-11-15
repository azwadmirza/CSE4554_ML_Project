    def save_spawn_weights(self, model):
        """
        Dump a temporary checkpoint after ddp ends to get weights out of the process
        :param model:
        :return:
        """
        if self.is_global_zero:
            path = os.path.join(self.default_root_dir, '__temp_weight_ddp_end.ckpt')
            self.save_checkpoint(path)
            return path