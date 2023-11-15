    def config_from_adapter(self, adapter):
        super().config_from_adapter(adapter)
        self.num_classes = adapter.num_classes
        self.loss = self.infer_loss()