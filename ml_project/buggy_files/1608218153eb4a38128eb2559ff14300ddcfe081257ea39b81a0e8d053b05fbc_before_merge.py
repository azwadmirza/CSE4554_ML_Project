def search_multiple_requests(requests, result_container, start_time, timeout_limit):
    search_id = uuid4().__str__()

    for engine_name, query, request_params in requests:
        th = threading.Thread(
            target=search_one_request_safe,
            args=(engine_name, query, request_params, result_container, start_time, timeout_limit),
            name=search_id,
        )
        th._engine_name = engine_name
        th.start()

    for th in threading.enumerate():
        if th.name == search_id:
            remaining_time = max(0.0, timeout_limit - (time() - start_time))
            th.join(remaining_time)
            if th.isAlive():
                result_container.add_unresponsive_engine((th._engine_name, gettext('timeout')))
                logger.warning('engine timeout: {0}'.format(th._engine_name))