    def __rdiv__(self, other: Metric) -> Metric:
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x, y: x.__div__(y), other, self)