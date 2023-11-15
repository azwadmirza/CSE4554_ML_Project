    def __init__(self, alphas=np.array([0.1, 1.0, 10.0]), fit_intercept=True,
                 normalize=False, score_func=None, loss_func=None, cv=None,
                 class_weight=None):
        super(RidgeClassifierCV, self).__init__(
            alphas=alphas, fit_intercept=fit_intercept, normalize=normalize,
            score_func=score_func, loss_func=loss_func, cv=cv)
        self.class_weight = class_weight