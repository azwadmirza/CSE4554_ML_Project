    def __sub__(self, other):
        from ignite.metrics import MetricsLambda
        return MetricsLambda(lambda x, y: x - y, self, other)