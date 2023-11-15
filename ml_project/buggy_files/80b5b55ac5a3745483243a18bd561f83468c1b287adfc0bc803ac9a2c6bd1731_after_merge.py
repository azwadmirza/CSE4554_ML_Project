    def __init__(self, sigma=0.1, n_bins=100, weight_function=None,
                 n_jobs=None):
        self.sigma = sigma
        self.n_bins = n_bins
        self.weight_function = weight_function
        self.n_jobs = n_jobs