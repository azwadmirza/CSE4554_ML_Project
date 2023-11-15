    def teardown(self):
        # replace the original fwd function
        self.trainer.model.forward = self.model_autocast_original_forward