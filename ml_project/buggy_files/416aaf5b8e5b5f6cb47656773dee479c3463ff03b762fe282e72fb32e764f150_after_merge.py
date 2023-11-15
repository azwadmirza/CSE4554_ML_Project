def init_to_median(site, num_samples=15, skip_param=False):
    """
    Initialize to the prior median.
    """
    if site['type'] == 'sample' and not site['is_observed']:
        if isinstance(site['fn'], dist.TransformedDistribution):
            fn = site['fn'].base_dist
        else:
            fn = site['fn']
        samples = sample('_init', fn, sample_shape=(num_samples,))
        return np.median(samples, axis=0)

    if site['type'] == 'param' and not skip_param:
        # return base value of param site
        constraint = site['kwargs'].pop('constraint', real)
        transform = biject_to(constraint)
        value = site['args'][0]
        if isinstance(transform, ComposeTransform):
            base_transform = transform.parts[0]
            value = base_transform(transform.inv(value))
        return value