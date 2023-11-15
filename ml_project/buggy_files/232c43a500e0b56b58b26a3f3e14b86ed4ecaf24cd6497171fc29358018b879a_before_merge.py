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

    best = fmin(fn=optimizer, space=SPACE, algo=tpe.suggest, max_evals=TOTAL_TRIES, trials=trials)

    # Improve best parameter logging display
    if best:
        best = space_eval(SPACE, best)

    logger.info('Best parameters:\n%s', json.dumps(best, indent=4))

    results = sorted(trials.results, key=itemgetter('loss'))
    logger.info('Best Result:\n%s', results[0]['result'])