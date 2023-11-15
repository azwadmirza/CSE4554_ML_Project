def _run_indexer(options):
    logging.info("Starting indexer %s:%s ..." % (options.host, options.port))
    # initialize crawler
    service = WaveformIndexer((options.host, options.port), MyHandler)
    service.log = logging
    try:
        # prepare paths
        if ',' in options.data:
            paths = options.data.split(',')
        else:
            paths = [options.data]
        paths = service._prepare_paths(paths)
        if not paths:
            return
        # prepare map file
        if options.mapping_file:
            with open(options.mapping_file, 'r') as f:
                data = f.readlines()
            mappings = parse_mapping_data(data)
            logging.info("Parsed %d lines from mapping file %s" %
                         (len(data), options.mapping_file))
        else:
            mappings = {}
        # create file queue and worker processes
        manager = multiprocessing.Manager()
        in_queue = manager.dict()
        work_queue = manager.list()
        out_queue = manager.list()
        log_queue = manager.list()
        # spawn processes
        for i in range(options.number_of_cpus):
            args = (i, in_queue, work_queue, out_queue, log_queue, mappings)
            p = multiprocessing.Process(target=worker, args=args)
            p.daemon = True
            p.start()
        # connect to database
        engine = create_engine(options.db_uri, encoding=native_str('utf-8'),
                               convert_unicode=True)
        metadata = Base.metadata
        # recreate database
        if options.drop_database:
            metadata.drop_all(engine, checkfirst=True)
        metadata.create_all(engine, checkfirst=True)
        # initialize database + options
        _session = sessionmaker(bind=engine)
        service.session = _session
        service.options = options
        service.mappings = mappings
        # set queues
        service.input_queue = in_queue
        service.work_queue = work_queue
        service.output_queue = out_queue
        service.log_queue = log_queue
        service.paths = paths
        service._reset_walker()
        service._step_walker()
        service.serve_forever(options.poll_interval)
    except KeyboardInterrupt:
        quit()
    logging.info("Indexer stopped.")