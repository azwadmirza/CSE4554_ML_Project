def combat(
    adata: AnnData,
    key: str = 'batch',
    covariates: Optional[Collection[str]] = None,
    inplace: bool = True,
) -> Union[AnnData, np.ndarray, None]:
    """\
    ComBat function for batch effect correction [Johnson07]_ [Leek12]_
    [Pedersen12]_.

    Corrects for batch effects by fitting linear models, gains statistical power
    via an EB framework where information is borrowed across genes.
    This uses the implementation `combat.py`_ [Pedersen12]_.

    .. _combat.py: https://github.com/brentp/combat.py

    Parameters
    ----------
    adata
        Annotated data matrix
    key
        Key to a categorical annotation from :attr:`~anndata.AnnData.obs`
        that will be used for batch effect removal.
    covariates
        Additional covariates besides the batch variable such as adjustment
        variables or biological condition. This parameter refers to the design
        matrix `X` in Equation 2.1 in [Johnson07]_ and to the `mod` argument in
        the original combat function in the sva R package.
        Note that not including covariates may introduce bias or lead to the
        removal of biological signal in unbalanced designs.
    inplace
        Whether to replace adata.X or to return the corrected data

    Returns
    -------
    Depending on the value of `inplace`, either returns the corrected matrix or
    or modifies `adata.X`.
    """

    # check the input
    if key not in adata.obs_keys():
        raise ValueError('Could not find the key {!r} in adata.obs'.format(key))

    if covariates is not None:
        cov_exist = np.isin(covariates, adata.obs_keys())
        if np.any(~cov_exist):
            missing_cov = np.array(covariates)[~cov_exist].tolist()
            raise ValueError('Could not find the covariate(s) {!r} in adata.obs'.format(missing_cov))

        if key in covariates:
            raise ValueError('Batch key and covariates cannot overlap')

        if len(covariates) != len(set(covariates)):
            raise ValueError('Covariates must be unique')

    # only works on dense matrices so far
    if issparse(adata.X):
        X = adata.X.A.T
    else:
        X = adata.X.T
    data = pd.DataFrame(
        data=X,
        index=adata.var_names,
        columns=adata.obs_names,
    )

    sanitize_anndata(adata)

    # construct a pandas series of the batch annotation
    model = adata.obs[[key] + (covariates if covariates else [])]
    batch_info = model.groupby(key).indices.values()
    n_batch = len(batch_info)
    n_batches = np.array([len(v) for v in batch_info])
    n_array = float(sum(n_batches))

    # standardize across genes using a pooled variance estimator
    logg.info("Standardizing Data across genes.\n")
    s_data, design, var_pooled, stand_mean = _standardize_data(model, data, key)

    # fitting the parameters on the standardized data
    logg.info("Fitting L/S model and finding priors\n")
    batch_design = design[design.columns[:n_batch]]
    # first estimate of the additive batch effect
    gamma_hat = np.dot(np.dot(la.inv(np.dot(batch_design.T, batch_design)), batch_design.T), s_data.T)
    delta_hat = []

    # first estimate for the multiplicative batch effect
    for i, batch_idxs in enumerate(batch_info):
        delta_hat.append(s_data.iloc[:, batch_idxs].var(axis=1))

    # empirically fix the prior hyperparameters
    gamma_bar = gamma_hat.mean(axis=1)
    t2 = gamma_hat.var(axis=1)
    # a_prior and b_prior are the priors on lambda and theta from Johnson and Li (2006)
    a_prior = list(map(_aprior, delta_hat))
    b_prior = list(map(_bprior, delta_hat))

    logg.info("Finding parametric adjustments\n")
    # gamma star and delta star will be our empirical bayes (EB) estimators
    # for the additive and multiplicative batch effect per batch and cell
    gamma_star, delta_star = [], []
    for i, batch_idxs in enumerate(batch_info):
        # temp stores our estimates for the batch effect parameters.
        # temp[0] is the additive batch effect
        # temp[1] is the multiplicative batch effect
        gamma, delta = _it_sol(
            s_data.iloc[:, batch_idxs].values,
            gamma_hat[i],
            delta_hat[i].values,
            gamma_bar[i],
            t2[i],
            a_prior[i],
            b_prior[i],
        )

        gamma_star.append(gamma)
        delta_star.append(delta)

    logg.info("Adjusting data\n")
    bayesdata = s_data
    gamma_star = np.array(gamma_star)
    delta_star = np.array(delta_star)

    # we now apply the parametric adjustment to the standardized data from above
    # loop over all batches in the data
    for j, batch_idxs in enumerate(batch_info):
        # we basically substract the additive batch effect, rescale by the ratio
        # of multiplicative batch effect to pooled variance and add the overall gene
        # wise mean
        dsq = np.sqrt(delta_star[j,:])
        dsq = dsq.reshape((len(dsq), 1))
        denom =  np.dot(dsq, np.ones((1, n_batches[j])))
        numer = np.array(bayesdata.iloc[:, batch_idxs] - np.dot(batch_design.iloc[batch_idxs], gamma_star).T)
        bayesdata.iloc[:, batch_idxs] = numer / denom

    vpsq = np.sqrt(var_pooled).reshape((len(var_pooled), 1))
    bayesdata = bayesdata * np.dot(vpsq, np.ones((1, int(n_array)))) + stand_mean

    # put back into the adata object or return
    if inplace:
        adata.X = bayesdata.values.transpose()
    else:
        return bayesdata.values.transpose()