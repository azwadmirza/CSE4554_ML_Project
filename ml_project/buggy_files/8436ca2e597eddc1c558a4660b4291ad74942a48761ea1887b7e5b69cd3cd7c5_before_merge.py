def predict(model, data, session=None, run_kwargs=None, run=True):
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

    op = XGBPredict(data=data, model=model, gpu=data.op.gpu, output_types=output_types)
    result = op()
    if run:
        result.execute(session=session, **(run_kwargs or dict()))
    return result