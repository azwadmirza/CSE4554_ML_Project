    def on_load_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        self.dataset_parameters = checkpoint.get("dataset_parameters", None)
        self.loss = cloudpickle.loads(checkpoint["loss"])
        self.output_transformer = cloudpickle.loads(checkpoint["output_transformer"])