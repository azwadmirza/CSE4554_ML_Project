    def __getitem__(self, index: Any):
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x: x[index], self)