def svd_training(params):
    """
    Train Surprise SVD using the given hyper-parameters
    """
    logger.debug("Start training...")
    train_data = pd.read_pickle(path=os.path.join(params['datastore'], params['train_datapath']))
    validation_data = pd.read_pickle(path=os.path.join(params['datastore'], params['validation_datapath']))

    svd_params = {p: params[p] for p in ['random_state', 'n_epochs', 'verbose', 'biased', 'n_factors', 'init_mean',
                                         'init_std_dev', 'lr_all', 'reg_all', 'lr_bu', 'lr_bi', 'lr_pu', 'lr_qi',
                                         'reg_bu', 'reg_bi', 'reg_pu', 'reg_qi']}
    svd = surprise.SVD(**svd_params)

    train_set = surprise.Dataset.load_from_df(train_data, reader=surprise.Reader(params['surprise_reader'])) \
        .build_full_trainset()
    svd.fit(train_set)

    logger.debug("Evaluating...")

    metrics_dict = {}
    rating_metrics = params['rating_metrics']
    if len(rating_metrics) > 0:
        predictions = compute_rating_predictions(svd, validation_data, usercol=params['usercol'],
                                                 itemcol=params['itemcol'])
        for metric in rating_metrics:
            result = getattr(evaluation, metric)(validation_data, predictions)
            logger.debug("%s = %g", metric, result)
            if metric == params['primary_metric']:
                metrics_dict['default'] = result
            else:
                metrics_dict[metric] = result

    ranking_metrics = params['ranking_metrics']
    if len(ranking_metrics) > 0:
        all_predictions = compute_ranking_predictions(svd, train_data, usercol=params['usercol'],
                                                      itemcol=params['itemcol'],
                                                      recommend_seen=params['recommend_seen'])
        k = params['k']
        for metric in ranking_metrics:
            result = getattr(evaluation, metric)(validation_data, all_predictions, col_prediction='prediction', k=k)
            logger.debug("%s@%d = %g", metric, k, result)
            if metric == params['primary_metric']:
                metrics_dict['default'] = result
            else:
                metrics_dict[metric] = result

    if len(ranking_metrics) == 0 and len(rating_metrics) == 0:
        raise ValueError("No metrics were specified.")

    # Report the metrics
    nni.report_final_result(metrics_dict)

    # Save the metrics in a JSON file
    output_dir = os.environ.get('NNI_OUTPUT_DIR')
    with open(os.path.join(output_dir, 'metrics.json'), 'w') as fp:
        temp_dict = metrics_dict.copy()
        temp_dict[params['primary_metric']] = temp_dict.pop('default')
        json.dump(temp_dict, fp)

    return svd