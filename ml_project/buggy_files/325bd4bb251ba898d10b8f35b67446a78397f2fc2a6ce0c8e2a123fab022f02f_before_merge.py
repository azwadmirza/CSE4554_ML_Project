    def __init__(self, estimator, step=1, cv=None, scoring=None,
                 estimator_params={}, verbose=0):
        self.estimator = estimator
        self.step = step
        self.cv = cv
        self.scoring = scoring
        self.estimator_params = estimator_params
        self.verbose = verbose