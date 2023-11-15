    def on_save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        checkpoint["dataset_parameters"] = getattr(
            self, "dataset_parameters", None
        )  # add dataset parameters for making fast predictions
        checkpoint["loss"] = cloudpickle.dumps(self.loss)  # restore loss
        checkpoint["output_transformer"] = cloudpickle.dumps(self.output_transformer)  # restore output transformer
        # hyper parameters are passed as arguments directly and not as single dictionary
        checkpoint["hparams_name"] = "kwargs"