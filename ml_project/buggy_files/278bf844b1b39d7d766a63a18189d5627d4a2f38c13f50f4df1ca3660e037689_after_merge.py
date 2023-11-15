def _check_transformer(name, Transformer, X, y):
    if name in ('CCA', 'LocallyLinearEmbedding', 'KernelPCA') and _is_32bit():
        # Those transformers yield non-deterministic output when executed on
        # a 32bit Python. The same transformers are stable on 64bit Python.
        # FIXME: try to isolate a minimalistic reproduction case only depending
        # on numpy & scipy and/or maybe generate a test dataset that does not
        # cause such unstable behaviors.
        msg = name + ' is non deterministic on 32bit Python'
        raise SkipTest(msg)
    n_samples, n_features = np.asarray(X).shape
    # catch deprecation warnings
    with warnings.catch_warnings(record=True):
        transformer = Transformer()
    set_random_state(transformer)
    set_fast_parameters(transformer)

    # fit

    if name in CROSS_DECOMPOSITION:
        y_ = np.c_[y, y]
        y_[::2, 1] *= 2
    else:
        y_ = y

    transformer.fit(X, y_)
    X_pred = transformer.fit_transform(X, y=y_)
    if isinstance(X_pred, tuple):
        for x_pred in X_pred:
            assert_equal(x_pred.shape[0], n_samples)
    else:
        assert_equal(X_pred.shape[0], n_samples)

    if hasattr(transformer, 'transform'):
        if name in CROSS_DECOMPOSITION:
            X_pred2 = transformer.transform(X, y_)
            X_pred3 = transformer.fit_transform(X, y=y_)
        else:
            X_pred2 = transformer.transform(X)
            X_pred3 = transformer.fit_transform(X, y=y_)
        if isinstance(X_pred, tuple) and isinstance(X_pred2, tuple):
            for x_pred, x_pred2, x_pred3 in zip(X_pred, X_pred2, X_pred3):
                assert_array_almost_equal(
                    x_pred, x_pred2, 2,
                    "fit_transform and transform outcomes not consistent in %s"
                    % Transformer)
                assert_array_almost_equal(
                    x_pred, x_pred3, 2,
                    "consecutive fit_transform outcomes not consistent in %s"
                    % Transformer)
        else:
            assert_array_almost_equal(
                X_pred, X_pred2, 2,
                "fit_transform and transform outcomes not consistent in %s"
                % Transformer)
            assert_array_almost_equal(
                X_pred, X_pred3, 2,
                "consecutive fit_transform outcomes not consistent in %s"
                % Transformer)

        # raises error on malformed input for transform
        if hasattr(X, 'T'):
            # If it's not an array, it does not have a 'T' property
            assert_raises(ValueError, transformer.transform, X.T)