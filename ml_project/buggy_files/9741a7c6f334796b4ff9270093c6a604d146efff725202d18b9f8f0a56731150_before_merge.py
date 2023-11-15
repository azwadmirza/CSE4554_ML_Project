    def __getitem__(self, index: Any) -> Metric:
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x: x[index], self)