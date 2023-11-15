def augment_data(X_train, feature_types_metadata: FeatureTypesMetadata, augmentation_data=None, augment_method='spunge', augment_args=None):
    """ augment_method options: ['spunge', 'munge']
    """
    if augment_args is None:
        augment_args = {}
    if augmentation_data is not None:
        X_aug = augmentation_data
    else:
        if 'num_augmented_samples' not in augment_args:
            if 'max_size' not in augment_args:
                augment_args['max_size'] = np.inf
            augment_args['num_augmented_samples'] = int(min(augment_args['max_size'], augment_args['size_factor']*len(X_train)))

        if augment_method == 'spunge':
            X_aug = spunge_augment(X_train, feature_types_metadata, **augment_args)
        elif augment_method == 'munge':
            X_aug = munge_augment(X_train, feature_types_metadata, **augment_args)
        else:
            raise ValueError(f"unknown augment_method: {augment_method}")

    # return postprocess_augmented(X_aug, X_train)  # TODO: dropping duplicates is much more efficient, but may skew distribution for entirely-categorical data with few categories.
    logger.log(15, f"Augmented training dataset with {len(X_aug)} extra datapoints")
    return X_aug.reset_index(drop=True)