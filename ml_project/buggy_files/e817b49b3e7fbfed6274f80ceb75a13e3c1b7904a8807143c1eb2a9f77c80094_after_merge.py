def _standardize_data(
    model: pd.DataFrame, data: pd.DataFrame, batch_key: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    """\
    Standardizes the data per gene.

    The aim here is to make mean and variance be comparable across batches.

    Parameters
    --------
    model
        Contains the batch annotation
    data
        Contains the Data
    batch_key
        Name of the batch column in the model matrix

    Returns
    --------
    s_data
        Standardized Data
    design
        Batch assignment as one-hot encodings
    var_pooled
        Pooled variance per gene
    stand_mean
        Gene-wise mean
    """

    # compute the design matrix
    batch_items = model.groupby(batch_key).groups.items()
    batch_levels, batch_info = zip(*batch_items)
    n_batch = len(batch_info)
    n_batches = np.array([len(v) for v in batch_info])
    n_array = float(sum(n_batches))

    design = _design_matrix(model, batch_key, batch_levels)

    # compute pooled variance estimator
    B_hat = np.dot(np.dot(la.inv(np.dot(design.T, design)), design.T), data.T)
    grand_mean = np.dot((n_batches / n_array).T, B_hat[:n_batch, :])
    var_pooled = (data - np.dot(design, B_hat).T) ** 2
    var_pooled = np.dot(var_pooled, np.ones((int(n_array), 1)) / int(n_array))

    # Compute the means
    if np.sum(var_pooled == 0) > 0:
        print(f'Found {np.sum(var_pooled == 0)} genes with zero variance.')
    stand_mean = np.dot(
        grand_mean.T.reshape((len(grand_mean), 1)), np.ones((1, int(n_array)))
    )
    tmp = np.array(design.copy())
    tmp[:, :n_batch] = 0
    stand_mean += np.dot(tmp, B_hat).T

    # need to be a bit careful with the zero variance genes
    # just set the zero variance genes to zero in the standardized data
    s_data = np.where(
        var_pooled == 0,
        0,
        ((data - stand_mean) / np.dot(np.sqrt(var_pooled), np.ones((1, int(n_array))))),
    )
    s_data = pd.DataFrame(s_data, index=data.index, columns=data.columns)

    return s_data, design, var_pooled, stand_mean