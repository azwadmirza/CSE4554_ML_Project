def munge_augment(X, feature_metadata: FeatureMetadata, num_augmented_samples=10000, perturb_prob=0.5, s=1.0, **kwargs):
    """ Uses MUNGE algorithm to generate synthetic datapoints for learning to mimic teacher model in distillation: https://www.cs.cornell.edu/~caruana/compression.kdd06.pdf
        Args:
            num_augmented_samples: number of additional augmented data points to return
            perturb_prob: probability of perturbing each feature during augmentation. Set near 0 to ensure augmented sample distribution remains closer to real data.
            s: We noise numeric features by their std-dev divided by this factor (inverse of continuous_feature_noise). Set large to ensure augmented sample distribution remains closer to real data.
    """
    nn_dummy = TabularNeuralNetModel(path='nn_dummy', name='nn_dummy', problem_type=REGRESSION, eval_metric=mean_squared_error,
                                     hyperparameters={'num_dataloading_workers': 0, 'proc.embed_min_categories': np.inf},
                                     features = list(X.columns), feature_metadata=feature_metadata)
    processed_data = nn_dummy.process_train_data(df=nn_dummy.preprocess(X), labels=pd.Series([1]*len(X)), batch_size=nn_dummy.params['batch_size'],
                        num_dataloading_workers=0, impute_strategy=nn_dummy.params['proc.impute_strategy'],
                        max_category_levels=nn_dummy.params['proc.max_category_levels'], skew_threshold=nn_dummy.params['proc.skew_threshold'],
                        embed_min_categories=nn_dummy.params['proc.embed_min_categories'], use_ngram_features=nn_dummy.params['use_ngram_features'])
    X_vector = processed_data.dataset._data[processed_data.vectordata_index].asnumpy()
    processed_data = None
    nn_dummy = None
    gc.collect()

    neighbor_finder = NearestNeighbors(n_neighbors=2)
    neighbor_finder.fit(X_vector)
    neigh_dist, neigh_ind = neighbor_finder.kneighbors(X_vector)
    neigh_ind = neigh_ind[:,1]  # contains indices of nearest neighbors
    neigh_dist = None
    # neigh_dist = neigh_dist[:,1]  # contains distances to nearest neighbors
    neighbor_finder = None
    gc.collect()

    if perturb_prob > 1.0:
        raise ValueError("frac_perturb must be <= 1")
    logger.log(20, f"MUNGE: Augmenting training data with {num_augmented_samples} synthetic samples for distillation...")
    X = X.copy()
    X_aug = pd.concat([X.iloc[[0]].copy()]*num_augmented_samples)
    X_aug.reset_index(drop=True, inplace=True)
    continuous_types = ['float', 'int']
    continuous_featnames = feature_metadata.get_features(valid_raw_types=continuous_types)  # these features will have shuffled values with added noise
    for col in continuous_featnames:
        X_aug[col] = X_aug[col].astype(float)
        X[col] = X[col].astype(float)

    for i in range(num_augmented_samples):
        og_ind = i % len(X)
        augdata_i = X.iloc[og_ind].copy()
        neighbor_i = X.iloc[neigh_ind[og_ind]].copy()
        # dist_i = neigh_dist[og_ind]
        cols_toperturb = np.random.choice(list(X.columns), size=np.random.binomial(X.shape[1], p=perturb_prob, size=1)[0], replace=False)
        for col in cols_toperturb:
            new_val = neighbor_i[col]
            if col in continuous_featnames:
                new_val += np.random.normal(scale=np.abs(augdata_i[col]-new_val)/s)
            augdata_i[col] = new_val
        X_aug.iloc[i] = augdata_i

    return X_aug