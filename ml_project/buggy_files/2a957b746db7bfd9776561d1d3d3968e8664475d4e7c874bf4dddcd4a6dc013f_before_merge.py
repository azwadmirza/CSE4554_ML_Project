    def hparams(self, hp: Union[dict, Namespace, Any]):
        self.save_hyperparameters(hp, frame=inspect.currentframe().f_back.f_back)