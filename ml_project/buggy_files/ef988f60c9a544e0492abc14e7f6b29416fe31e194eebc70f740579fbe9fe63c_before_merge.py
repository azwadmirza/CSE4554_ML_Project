    def __mul__(self, other: Metric) -> Metric:
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x, y: x * y, self, other)