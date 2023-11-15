def balanced_accuracy(solution, prediction):
    y_type, solution, prediction = _check_targets(solution, prediction)

    if y_type not in ["binary", "multiclass", 'multilabel-indicator']:
        raise ValueError(f"{y_type} is not supported")

    if y_type == 'binary':
        # Do not transform into any multiclass representation
        pass

    elif y_type == 'multiclass':
        n = len(solution)
        unique_sol, encoded_sol = np.unique(solution, return_inverse=True)
        unique_pred, encoded_pred = np.unique(prediction, return_inverse=True)
        classes = np.unique(np.concatenate((unique_sol, unique_pred)))
        map_sol = np.array([np.where(classes==c)[0][0] for c in unique_sol])
        map_pred = np.array([np.where(classes==c)[0][0] for c in unique_pred])
        # one hot encoding
        sol_ohe = np.zeros((n, len(classes)))
        pred_ohe = np.zeros((n, len(classes)))
        sol_ohe[np.arange(n), map_sol[encoded_sol]] = 1
        pred_ohe[np.arange(n), map_pred[encoded_pred]] = 1
        solution = sol_ohe
        prediction = pred_ohe

    elif y_type == 'multilabel-indicator':
        solution = solution.toarray()
        prediction = prediction.toarray()
    else:
        raise NotImplementedError(f'bac_metric does not support task type {y_type}')

    fn = np.sum(np.multiply(solution, (1 - prediction)), axis=0, dtype=float)
    tp = np.sum(np.multiply(solution, prediction), axis=0, dtype=float)
    # Bounding to avoid division by 0
    eps = 1e-15
    tp = np.maximum(eps, tp)
    pos_num = np.maximum(eps, tp + fn)
    tpr = tp / pos_num  # true positive rate (sensitivity)

    if y_type in ('binary', 'multilabel-indicator'):
        tn = np.sum(
            np.multiply((1 - solution), (1 - prediction)),
            axis=0, dtype=float
        )
        fp = np.sum(
            np.multiply((1 - solution), prediction),
            axis=0, dtype=float
        )
        tn = np.maximum(eps, tn)
        neg_num = np.maximum(eps, tn + fp)
        tnr = tn / neg_num  # true negative rate (specificity)
        bac = 0.5 * (tpr + tnr)
    elif y_type == 'multiclass':
        bac = tpr
    else:
        raise ValueError(y_type)

    return np.mean(bac)  # average over all classes