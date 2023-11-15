def train(params, train_set, eval_sets=None, **kwargs):
    eval_sets = eval_sets or []
    model_type = kwargs.pop('model_type', LGBMModelType.CLASSIFIER)

    evals_result = kwargs.pop('evals_result', dict())
    session = kwargs.pop('session', None)
    run_kwargs = kwargs.pop('run_kwargs', dict())
    timeout = kwargs.pop('timeout', 120)
    base_port = kwargs.pop('base_port', None)

    aligns = align_data_set(train_set)
    for eval_set in eval_sets:
        aligns += align_data_set(eval_set)

    aligned_iter = iter(ExecutableTuple(aligns).execute(session))
    datas, labels, sample_weights, init_scores = [], [], [], []
    for dataset in [train_set] + eval_sets:
        train_kw = dict()
        for arg in ['data', 'label', 'sample_weight', 'init_score']:
            if getattr(dataset, arg) is not None:
                train_kw[arg] = next(aligned_iter)
            else:
                train_kw[arg] = None

        datas.append(train_kw['data'])
        labels.append(train_kw['label'])
        sample_weights.append(train_kw['sample_weight'])
        init_scores.append(train_kw['init_score'])

    op = LGBMTrain(params=params, data=datas[0], label=labels[0], sample_weight=sample_weights[0],
                   init_score=init_scores[0], eval_datas=datas[1:], eval_labels=labels[1:],
                   eval_weights=sample_weights[1:], eval_init_score=init_scores[1:],
                   model_type=model_type, timeout=timeout, lgbm_port=base_port, kwds=kwargs)
    ret = op().execute(session=session, **run_kwargs).fetch(session=session)

    bst = pickle.loads(ret)
    evals_result.update(bst.evals_result_ or {})
    return bst