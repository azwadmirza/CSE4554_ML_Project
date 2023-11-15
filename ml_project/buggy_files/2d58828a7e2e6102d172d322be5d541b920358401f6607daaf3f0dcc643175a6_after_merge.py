    def __init__(self, *, alpha=1.0, fit_prior=True, class_prior=None,
                 min_categories=None):
        self.alpha = alpha
        self.fit_prior = fit_prior
        self.class_prior = class_prior
        self.min_categories = min_categories