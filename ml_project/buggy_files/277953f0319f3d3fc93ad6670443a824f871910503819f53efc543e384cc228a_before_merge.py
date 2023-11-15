    def __init__(self, estimator, n_features_to_select=None, step=1,
                 estimator_params={}, verbose=0):
        self.estimator = estimator
        self.n_features_to_select = n_features_to_select
        self.step = step
        self.estimator_params = estimator_params
        self.verbose = verbose