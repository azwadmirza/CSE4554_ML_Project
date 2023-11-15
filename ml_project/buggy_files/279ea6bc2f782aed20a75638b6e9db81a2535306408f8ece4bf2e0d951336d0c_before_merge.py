    def load_spawn_weights(self, original_model):
        """
        Load the temp weights saved in the process
        To recover the trained model from the ddp process we load the saved weights
        :param model:
        :return:
        """
        # load weights saved in ddp
        path = os.path.join(self.default_save_path, '__temp_weight_ddp_end.ckpt')
        loaded_model = original_model.__class__.load_from_checkpoint(path)

        # copy loaded weights to old model
        original_model.load_state_dict(loaded_model.state_dict())

        # remove ddp weights
        os.remove(path)

        return loaded_model