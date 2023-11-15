def predict(model, data, output_margin=False, ntree_limit=None,
            validate_features=True, base_margin=None,
            session=None, run_kwargs=None, run=True):
    from xgboost import Booster

    data = check_data(data)
    if not isinstance(model, Booster):
        raise TypeError(f'model has to be a xgboost.Booster, got {type(model)} instead')

    num_class = model.attr('num_class')
    if isinstance(data, TENSOR_TYPE):
        output_types = [OutputType.tensor]
    elif num_class is not None:
        output_types = [OutputType.dataframe]
    else:
        output_types = [OutputType.series]

    kwargs = {
        'output_margin': output_margin,
        'ntree_limit': ntree_limit,
        'validate_features': validate_features,
        'base_margin': base_margin
    }
    op = XGBPredict(data=data, model=model, kwargs=kwargs,
                    gpu=data.op.gpu, output_types=output_types)
    result = op()
    if run:
        result.execute(session=session, **(run_kwargs or dict()))
    return result