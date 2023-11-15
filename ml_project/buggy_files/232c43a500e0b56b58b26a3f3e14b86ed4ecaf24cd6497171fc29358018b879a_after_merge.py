def start(args):
    global TOTAL_TRIES, PROCESSED, SPACE
    TOTAL_TRIES = args.epochs

    exchange._API = Bittrex({'key': '', 'secret': ''})

    # Initialize logger
    logging.basicConfig(
        level=args.loglevel,
        format='\n%(message)s',
    )

    logger.info('Using config: %s ...', args.config)
    config = load_config(args.config)
    pairs = config['exchange']['pair_whitelist']
    PROCESSED = optimize.preprocess(optimize.load_data(
        args.datadir, pairs=pairs, ticker_interval=args.ticker_interval))

    if args.mongodb:
        logger.info('Using mongodb ...')
        logger.info('Start scripts/start-mongodb.sh and start-hyperopt-worker.sh manually!')

        db_name = 'freqtrade_hyperopt'
        trials = MongoTrials('mongo://127.0.0.1:1234/{}/jobs'.format(db_name), exp_key='exp1')
    else:
        trials = Trials()

    try:
        best_parameters = fmin(
            fn=optimizer,
            space=SPACE,
            algo=tpe.suggest,
            max_evals=TOTAL_TRIES,
            trials=trials
        )

        results = sorted(trials.results, key=itemgetter('loss'))
        best_result = results[0]['result']

    except ValueError:
        best_parameters = {}
        best_result = 'Sorry, Hyperopt was not able to find good parameters. Please ' \
                      'try with more epochs (param: -e).'

    # Improve best parameter logging display
    if best_parameters:
        best_parameters = space_eval(SPACE, best_parameters)

    logger.info('Best parameters:\n%s', json.dumps(best_parameters, indent=4))
    logger.info('Best Result:\n%s', best_result)