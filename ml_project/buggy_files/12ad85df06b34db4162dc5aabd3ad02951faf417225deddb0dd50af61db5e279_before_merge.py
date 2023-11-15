def task_run(args, dag=None):
    """Runs a single task instance"""
    # Load custom airflow config
    if args.cfg_path:
        with open(args.cfg_path, 'r') as conf_file:
            conf_dict = json.load(conf_file)

        if os.path.exists(args.cfg_path):
            os.remove(args.cfg_path)

        conf.read_dict(conf_dict, source=args.cfg_path)
        settings.configure_vars()

    # IMPORTANT, have to use the NullPool, otherwise, each "run" command may leave
    # behind multiple open sleeping connections while heartbeating, which could
    # easily exceed the database connection limit when
    # processing hundreds of simultaneous tasks.
    settings.configure_orm(disable_connection_pool=True)

    if dag and args.pickle:
        raise AirflowException("You cannot use the --pickle option when using DAG.cli() method.")
    elif args.pickle:
        print(f'Loading pickle id: {args.pickle}')
        dag = get_dag_by_pickle(args.pickle)
    elif not dag:
        dag = get_dag(args.subdir, args.dag_id)
    else:
        # Use DAG from parameter
        pass

    task = dag.get_task(task_id=args.task_id)
    ti = TaskInstance(task, args.execution_date)
    ti.init_run_context(raw=args.raw)

    hostname = get_hostname()

    print(f"Running {ti} on host {hostname}")

    if args.interactive:
        _run_task_by_selected_method(args, dag, ti)
    else:
        if settings.DONOT_MODIFY_HANDLERS:
            with redirect_stdout(StreamLogWriter(ti.log, logging.INFO)), \
                    redirect_stderr(StreamLogWriter(ti.log, logging.WARN)):
                _run_task_by_selected_method(args, dag, ti)
        else:
            # Get all the Handlers from 'airflow.task' logger
            # Add these handlers to the root logger so that we can get logs from
            # any custom loggers defined in the DAG
            airflow_logger_handlers = logging.getLogger('airflow.task').handlers
            root_logger = logging.getLogger()
            root_logger_handlers = root_logger.handlers

            # Remove all handlers from Root Logger to avoid duplicate logs
            for handler in root_logger_handlers:
                root_logger.removeHandler(handler)

            for handler in airflow_logger_handlers:
                root_logger.addHandler(handler)
            root_logger.setLevel(logging.getLogger('airflow.task').level)

            with redirect_stdout(StreamLogWriter(ti.log, logging.INFO)), \
                    redirect_stderr(StreamLogWriter(ti.log, logging.WARN)):
                _run_task_by_selected_method(args, dag, ti)

            # We need to restore the handlers to the loggers as celery worker process
            # can call this command multiple times,
            # so if we don't reset this then logs from next task would go to the wrong place
            for handler in airflow_logger_handlers:
                root_logger.removeHandler(handler)
            for handler in root_logger_handlers:
                root_logger.addHandler(handler)

    logging.shutdown()