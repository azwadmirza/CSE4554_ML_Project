    def __rmul__(self, other):
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x, y: x * y, other, self)