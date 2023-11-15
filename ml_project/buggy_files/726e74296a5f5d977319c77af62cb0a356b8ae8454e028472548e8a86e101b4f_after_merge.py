def parametric(subposteriors, diagonal=False):
    """
    Merges subposteriors following (embarrassingly parallel) parametric Monte Carlo algorithm.

    **References:**

    1. *Asymptotically Exact, Embarrassingly Parallel MCMC*,
       Willie Neiswanger, Chong Wang, Eric Xing

    :param list subposteriors: a list in which each element is a collection of samples.
    :param bool diagonal: whether to compute weights using variance or covariance, defaults to
        `False` (using covariance).
    :return: the estimated mean and variance/covariance parameters of the joined posterior
    """
    joined_subposteriors = tree_multimap(lambda *args: np.stack(args), *subposteriors)
    joined_subposteriors = vmap(vmap(lambda sample: ravel_pytree(sample)[0]))(joined_subposteriors)

    submeans = np.mean(joined_subposteriors, axis=1)
    if diagonal:
        # NB: jax.numpy.var does not support ddof=1, so we do it manually
        weights = vmap(lambda x: 1 / np.var(x, ddof=1, axis=0))(joined_subposteriors)
        var = 1 / np.sum(weights, axis=0)
        normalized_weights = var * weights

        # comparing to consensus implementation, we compute weighted mean here
        mean = np.einsum('ij,ij->j', normalized_weights, submeans)
        return mean, var
    else:
        weights = vmap(lambda x: np.linalg.inv(np.cov(x.T)))(joined_subposteriors)
        cov = np.linalg.inv(np.sum(weights, axis=0))
        normalized_weights = np.matmul(cov, weights)

        # comparing to consensus implementation, we compute weighted mean here
        mean = np.einsum('ijk,ik->j', normalized_weights, submeans)
        return mean, cov