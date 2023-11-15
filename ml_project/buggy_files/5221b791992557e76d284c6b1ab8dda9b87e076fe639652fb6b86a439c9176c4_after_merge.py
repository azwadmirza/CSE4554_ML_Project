def consensus(subposteriors, num_draws=None, diagonal=False, rng=None):
    """
    Merges subposteriors following consensus Monte Carlo algorithm.

    **References:**

    1. *Bayes and big data: The consensus Monte Carlo algorithm*,
       Steven L. Scott, Alexander W. Blocker, Fernando V. Bonassi, Hugh A. Chipman,
       Edward I. George, Robert E. McCulloch

    :param list subposteriors: a list in which each element is a collection of samples.
    :param int num_draws: number of draws from the merged posterior.
    :param bool diagonal: whether to compute weights using variance or covariance, defaults to
        `False` (using covariance).
    :param jax.random.PRNGKey rng: source of the randomness, defaults to `jax.random.PRNGKey(0)`.
    :return: if `num_draws` is None, merges subposteriors without resampling; otherwise, returns
        a collection of `num_draws` samples with the same data structure as each subposterior.
    """
    # stack subposteriors
    joined_subposteriors = tree_multimap(lambda *args: np.stack(args), *subposteriors)
    # shape of joined_subposteriors: n_subs x n_samples x sample_shape
    joined_subposteriors = vmap(vmap(lambda sample: ravel_pytree(sample)[0]))(joined_subposteriors)

    if num_draws is not None:
        rng = random.PRNGKey(0) if rng is None else rng
        # randomly gets num_draws from subposteriors
        n_subs = len(subposteriors)
        n_samples = tree_flatten(subposteriors[0])[0][0].shape[0]
        # shape of draw_idxs: n_subs x num_draws x sample_shape
        draw_idxs = random.randint(rng, shape=(n_subs, num_draws), minval=0, maxval=n_samples)
        joined_subposteriors = vmap(lambda x, idx: x[idx])(joined_subposteriors, draw_idxs)

    if diagonal:
        # compute weights for each subposterior (ref: Section 3.1 of [1])
        weights = vmap(lambda x: 1 / np.var(x, ddof=1, axis=0))(joined_subposteriors)
        normalized_weights = weights / np.sum(weights, axis=0)
        # get weighted samples
        samples_flat = np.einsum('ij,ikj->kj', normalized_weights, joined_subposteriors)
    else:
        weights = vmap(lambda x: np.linalg.inv(np.cov(x.T)))(joined_subposteriors)
        normalized_weights = np.matmul(np.linalg.inv(np.sum(weights, axis=0)), weights)
        samples_flat = np.einsum('ijk,ilk->lj', normalized_weights, joined_subposteriors)

    # unravel_fn acts on 1 sample of a subposterior
    _, unravel_fn = ravel_pytree(tree_map(lambda x: x[0], subposteriors[0]))
    return vmap(lambda x: unravel_fn(x))(samples_flat)