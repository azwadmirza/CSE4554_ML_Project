def mcmc(num_warmup, num_samples, init_params, num_chains=1, sampler='hmc',
         constrain_fn=None, print_summary=True, **sampler_kwargs):
    """
    Convenience wrapper for MCMC samplers -- runs warmup, prints
    diagnostic summary and returns a collections of samples
    from the posterior.

    :param num_warmup: Number of warmup steps.
    :param num_samples: Number of samples to generate from the Markov chain.
    :param init_params: Initial parameters to begin sampling. The type can
        must be consistent with the input type to `potential_fn`.
    :param sampler: currently, only `hmc` is implemented (default).
    :param constrain_fn: Callable that converts a collection of unconstrained
        sample values returned from the sampler to constrained values that
        lie within the support of the sample sites.
    :param print_summary: Whether to print diagnostics summary for
        each sample site. Default is ``True``.
    :param `**sampler_kwargs`: Sampler specific keyword arguments.

         - *HMC*: Refer to :func:`~numpyro.mcmc.hmc` and
           :func:`~numpyro.mcmc.hmc.init_kernel` for accepted arguments. Note
           that all arguments must be provided as keywords.

    :return: collection of samples from the posterior.

    .. testsetup::

       import jax
       from jax import random
       import jax.numpy as np
       import numpyro.distributions as dist
       from numpyro.handlers import sample
       from numpyro.hmc_util import initialize_model
       from numpyro.mcmc import hmc
       from numpyro.util import fori_collect

    .. doctest::

        >>> true_coefs = np.array([1., 2., 3.])
        >>> data = random.normal(random.PRNGKey(2), (2000, 3))
        >>> dim = 3
        >>> labels = dist.Bernoulli(logits=(true_coefs * data).sum(-1)).sample(random.PRNGKey(3))
        >>>
        >>> def model(data, labels):
        ...     coefs_mean = np.zeros(dim)
        ...     coefs = sample('beta', dist.Normal(coefs_mean, np.ones(3)))
        ...     intercept = sample('intercept', dist.Normal(0., 10.))
        ...     return sample('y', dist.Bernoulli(logits=(coefs * data + intercept).sum(-1)), obs=labels)
        >>>
        >>> init_params, potential_fn, constrain_fn = initialize_model(random.PRNGKey(0), model,
        ...                                                            data, labels)
        >>> num_warmup, num_samples = 1000, 1000
        >>> samples = mcmc(num_warmup, num_samples, init_params,
        ...                potential_fn=potential_fn,
        ...                constrain_fn=constrain_fn)  # doctest: +SKIP
        warmup: 100%|██████████| 1000/1000 [00:09<00:00, 109.40it/s, 1 steps of size 5.83e-01. acc. prob=0.79]
        sample: 100%|██████████| 1000/1000 [00:00<00:00, 1252.39it/s, 1 steps of size 5.83e-01. acc. prob=0.85]


                           mean         sd       5.5%      94.5%      n_eff       Rhat
            coefs[0]       0.96       0.07       0.85       1.07     455.35       1.01
            coefs[1]       2.05       0.09       1.91       2.20     332.00       1.01
            coefs[2]       3.18       0.13       2.96       3.37     320.27       1.00
           intercept      -0.03       0.02      -0.06       0.00     402.53       1.00
    """
    sequential_chain = False
    if xla_bridge.device_count() < num_chains:
        sequential_chain = True
        warnings.warn('There are not enough devices to run parallel chains: expected {} but got {}.'
                      ' Chains will be drawn sequentially. If you are running `mcmc` in CPU,'
                      ' consider to disable XLA intra-op parallelism by setting the environment'
                      ' flag "XLA_FLAGS=--xla_force_host_platform_device_count={}".'
                      .format(num_chains, xla_bridge.device_count(), num_chains))
    progbar = sampler_kwargs.pop('progbar', True)
    if num_chains > 1:
        progbar = False

    if sampler == 'hmc':
        if constrain_fn is None:
            constrain_fn = identity
        potential_fn = sampler_kwargs.pop('potential_fn')
        kinetic_fn = sampler_kwargs.pop('kinetic_fn', None)
        algo = sampler_kwargs.pop('algo', 'NUTS')
        if num_chains > 1:
            rngs = sampler_kwargs.pop('rng', vmap(PRNGKey)(np.arange(num_chains)))
        else:
            rng = sampler_kwargs.pop('rng', PRNGKey(0))

        init_kernel, sample_kernel = hmc(potential_fn, kinetic_fn, algo)
        if progbar:
            hmc_state = init_kernel(init_params, num_warmup, progbar=progbar, rng=rng,
                                    **sampler_kwargs)
            samples_flat = fori_collect(0, num_samples, sample_kernel, hmc_state,
                                        transform=lambda x: constrain_fn(x.z),
                                        progbar=progbar,
                                        diagnostics_fn=get_diagnostics_str,
                                        progbar_desc='sample')
            samples = tree_map(lambda x: x[np.newaxis, ...], samples_flat)
        else:
            def single_chain_mcmc(rng, init_params):
                hmc_state = init_kernel(init_params, num_warmup, run_warmup=False, rng=rng,
                                        **sampler_kwargs)
                samples = fori_collect(num_warmup, num_warmup + num_samples, sample_kernel, hmc_state,
                                       transform=lambda x: constrain_fn(x.z),
                                       progbar=progbar)
                return samples

            if num_chains == 1:
                samples_flat = single_chain_mcmc(rng, init_params)
                samples = tree_map(lambda x: x[np.newaxis, ...], samples_flat)
            else:
                if sequential_chain:
                    samples = lax.map(lambda args: single_chain_mcmc(*args), (rngs, init_params))
                else:
                    samples = pmap(single_chain_mcmc)(rngs, init_params)
                samples_flat = tree_map(lambda x: np.reshape(x, (-1,) + x.shape[2:]), samples)

        if print_summary:
            summary(samples)
        return samples_flat
    else:
        raise ValueError('sampler: {} not recognized'.format(sampler))