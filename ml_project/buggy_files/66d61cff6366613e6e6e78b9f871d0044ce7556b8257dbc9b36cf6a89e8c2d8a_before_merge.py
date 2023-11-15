def set_fast_parameters(estimator):
    # speed up some estimators
    params = estimator.get_params()
    if estimator.__class__.__name__ == 'OrthogonalMatchingPursuitCV':
        # FIXME: This test is unstable on Travis, see issue #3190.
        check_skip_travis()
    if ("n_iter" in params
            and estimator.__class__.__name__ != "TSNE"):
        estimator.set_params(n_iter=5)
    if "max_iter" in params:
        # NMF
        if estimator.max_iter is not None:
            estimator.set_params(max_iter=min(5, estimator.max_iter))
        # LinearSVR
        if estimator.__class__.__name__ == 'LinearSVR':
            estimator.set_params(max_iter=20)
    if "n_resampling" in params:
        # randomized lasso
        estimator.set_params(n_resampling=5)
    if "n_estimators" in params:
        # especially gradient boosting with default 100
        estimator.set_params(n_estimators=min(5, estimator.n_estimators))
    if "max_trials" in params:
        # RANSAC
        estimator.set_params(max_trials=10)
    if "n_init" in params:
        # K-Means
        estimator.set_params(n_init=2)

    if estimator.__class__.__name__ == "SelectFdr":
        # be tolerant of noisy datasets (not actually speed)
        estimator.set_params(alpha=.5)

    if estimator.__class__.__name__ == "TheilSenRegressor":
        estimator.max_subpopulation = 100

    if isinstance(estimator, BaseRandomProjection):
        # Due to the jl lemma and often very few samples, the number
        # of components of the random matrix projection will be probably
        # greater than the number of features.
        # So we impose a smaller number (avoid "auto" mode)
        estimator.set_params(n_components=1)

    if isinstance(estimator, SelectKBest):
        # SelectKBest has a default of k=10
        # which is more feature than we have in most case.
        estimator.set_params(k=1)