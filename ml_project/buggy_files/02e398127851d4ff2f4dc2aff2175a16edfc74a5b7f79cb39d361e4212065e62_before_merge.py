    def __init__(self, metric='landscape', metric_params=None, order=2.,
                 n_jobs=None):
        self.metric = metric
        self.metric_params = metric_params
        self.order = order
        self.n_jobs = n_jobs