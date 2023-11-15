def spunge_augment(X, feature_metadata: FeatureMetadata, num_augmented_samples=10000, frac_perturb=0.1, continuous_feature_noise=0.1, **kwargs):
    """ Generates synthetic datapoints for learning to mimic teacher model in distillation
        via simplified version of MUNGE strategy (that does not require near-neighbor search).

        Args:
            num_augmented_samples: number of additional augmented data points to return
            frac_perturb: fraction of features/examples that are perturbed during augmentation. Set near 0 to ensure augmented sample distribution remains closer to real data.
            continuous_feature_noise: we noise numeric features by this factor times their std-dev. Set near 0 to ensure augmented sample distribution remains closer to real data.
    """
    if frac_perturb > 1.0:
        raise ValueError("frac_perturb must be <= 1")
    logger.log(20, f"SPUNGE: Augmenting training data with {num_augmented_samples} synthetic samples for distillation...")
    num_feature_perturb = max(1, int(frac_perturb*len(X.columns)))
    X_aug = pd.concat([X.iloc[[0]].copy()]*num_augmented_samples)
    X_aug.reset_index(drop=True, inplace=True)
    continuous_types = ['float', 'int']
    continuous_featnames = feature_metadata.get_features(valid_raw_types=continuous_types)  # these features will have shuffled values with added noise

    for i in range(num_augmented_samples): # hot-deck sample some features per datapoint
        og_ind = i % len(X)
        augdata_i = X.iloc[og_ind].copy()
        num_feature_perturb_i = np.random.choice(range(1,num_feature_perturb+1))  # randomly sample number of features to perturb
        cols_toperturb = np.random.choice(list(X.columns), size=num_feature_perturb_i, replace=False)
        for feature in cols_toperturb:
            feature_data = X[feature]
            augdata_i[feature] = feature_data.sample(n=1).values[0]
        X_aug.iloc[i] = augdata_i

    for feature in X.columns:
        if feature in continuous_featnames:
            feature_data = X[feature]
            aug_data = X_aug[feature]
            noise = np.random.normal(scale=np.nanstd(feature_data)*continuous_feature_noise, size=num_augmented_samples)
            mask = np.random.binomial(n=1, p=frac_perturb, size=num_augmented_samples)
            aug_data = aug_data + noise*mask
            X_aug[feature] = pd.Series(aug_data, index=X_aug.index)

    return X_aug