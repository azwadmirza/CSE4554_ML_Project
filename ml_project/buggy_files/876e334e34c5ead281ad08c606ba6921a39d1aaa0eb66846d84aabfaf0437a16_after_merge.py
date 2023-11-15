    def sub_variational_strategies(self):
        if not hasattr(self, "_sub_variational_strategies_memo"):
            self._sub_variational_strategies_memo = [
                module.variational_strategy for module in self.model.modules()
                if isinstance(module, ApproximateGP)
            ]
        return self._sub_variational_strategies_memo