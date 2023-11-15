def execute_query(self, query, data_source_id, metadata):
    signal.signal(signal.SIGINT, signal_handler)
    start_time = time.time()

    logger.info("Loading data source (%d)...", data_source_id)

    # TODO: we should probably cache data sources in Redis
    data_source = models.DataSource.get_by_id(data_source_id)

    self.update_state(state='STARTED', meta={'start_time': start_time, 'custom_message': ''})

    logger.info("Executing query:\n%s", query)

    query_hash = gen_query_hash(query)
    query_runner = get_query_runner(data_source.type, data_source.options)

    if query_runner.annotate_query():
        metadata['Task ID'] = self.request.id
        metadata['Query Hash'] = query_hash
        metadata['Queue'] = self.request.delivery_info['routing_key']

        annotation = u", ".join([u"{}: {}".format(k, v) for k, v in metadata.iteritems()])

        logging.debug(u"Annotation: %s", annotation)

        annotated_query = u"/* {} */ {}".format(annotation, query)
    else:
        annotated_query = query

    with statsd_client.timer('query_runner.{}.{}.run_time'.format(data_source.type, data_source.name)):
        data, error = query_runner.run_query(annotated_query)

    run_time = time.time() - start_time
    logger.info("Query finished... data length=%s, error=%s", data and len(data), error)

    self.update_state(state='STARTED', meta={'start_time': start_time, 'error': error, 'custom_message': ''})

    # Delete query_hash
    redis_connection.delete(QueryTask._job_lock_id(query_hash, data_source.id))

    if not error:
        query_result, updated_query_ids = models.QueryResult.store_result(data_source.org_id, data_source.id, query_hash, query, data, run_time, utils.utcnow())
        for query_id in updated_query_ids:
            check_alerts_for_query.delay(query_id)
    else:
        raise QueryExecutionError(error)

    return query_result.id