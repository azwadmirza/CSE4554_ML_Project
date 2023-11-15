def execute_sql_statements(
    ctask,
    query_id,
    rendered_query,
    return_results=True,
    store_results=False,
    user_name=None,
    session=None,
    start_time=None,
    expand_data=False,
):
    """Executes the sql query returns the results."""
    if store_results and start_time:
        # only asynchronous queries
        stats_logger.timing("sqllab.query.time_pending", now_as_float() - start_time)

    query = get_query(query_id, session)
    payload = dict(query_id=query_id)
    database = query.database
    db_engine_spec = database.db_engine_spec
    db_engine_spec.patch()

    if database.allow_run_async and not results_backend:
        raise SqlLabException("Results backend isn't configured.")

    # Breaking down into multiple statements
    parsed_query = ParsedQuery(rendered_query)
    statements = parsed_query.get_statements()
    logging.info(f"Query {query_id}: Executing {len(statements)} statement(s)")

    logging.info(f"Query {query_id}: Set query to 'running'")
    query.status = QueryStatus.RUNNING
    query.start_running_time = now_as_float()
    session.commit()

    engine = database.get_sqla_engine(
        schema=query.schema,
        nullpool=True,
        user_name=user_name,
        source=sources.get("sql_lab", None),
    )
    # Sharing a single connection and cursor across the
    # execution of all statements (if many)
    with closing(engine.raw_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            statement_count = len(statements)
            for i, statement in enumerate(statements):
                # Check if stopped
                query = get_query(query_id, session)
                if query.status == QueryStatus.STOPPED:
                    return

                # Run statement
                msg = f"Running statement {i+1} out of {statement_count}"
                logging.info(f"Query {query_id}: {msg}")
                query.set_extra_json_key("progress", msg)
                session.commit()
                try:
                    cdf = execute_sql_statement(
                        statement, query, user_name, session, cursor
                    )
                except Exception as e:
                    msg = str(e)
                    if statement_count > 1:
                        msg = f"[Statement {i+1} out of {statement_count}] " + msg
                    payload = handle_query_error(msg, query, session, payload)
                    return payload

    # Success, updating the query entry in database
    query.rows = cdf.size
    query.progress = 100
    query.set_extra_json_key("progress", None)
    if query.select_as_cta:
        query.select_sql = database.select_star(
            query.tmp_table_name,
            limit=query.limit,
            schema=database.force_ctas_schema,
            show_cols=False,
            latest_partition=False,
        )
    query.end_time = now_as_float()

    data, selected_columns, all_columns, expanded_columns = _serialize_and_expand_data(
        cdf, db_engine_spec, store_results and results_backend_use_msgpack, expand_data
    )

    payload.update(
        {
            "status": QueryStatus.SUCCESS,
            "data": data,
            "columns": all_columns,
            "selected_columns": selected_columns,
            "expanded_columns": expanded_columns,
            "query": query.to_dict(),
        }
    )
    payload["query"]["state"] = QueryStatus.SUCCESS

    if store_results and results_backend:
        key = str(uuid.uuid4())
        logging.info(
            f"Query {query_id}: Storing results in results backend, key: {key}"
        )
        with stats_timing("sqllab.query.results_backend_write", stats_logger):
            with stats_timing(
                "sqllab.query.results_backend_write_serialization", stats_logger
            ):
                serialized_payload = _serialize_payload(
                    payload, results_backend_use_msgpack
                )
            cache_timeout = database.cache_timeout
            if cache_timeout is None:
                cache_timeout = config["CACHE_DEFAULT_TIMEOUT"]

            compressed = zlib_compress(serialized_payload)
            logging.debug(
                f"*** serialized payload size: {getsizeof(serialized_payload)}"
            )
            logging.debug(f"*** compressed payload size: {getsizeof(compressed)}")
            results_backend.set(key, compressed, cache_timeout)
        query.results_key = key

    query.status = QueryStatus.SUCCESS
    session.commit()

    if return_results:
        return payload