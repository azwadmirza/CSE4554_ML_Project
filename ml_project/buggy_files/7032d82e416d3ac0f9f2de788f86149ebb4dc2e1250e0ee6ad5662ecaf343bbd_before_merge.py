def search_one_http_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    # set timeout for all HTTP requests
    requests_lib.set_timeout_for_thread(timeout_limit, start_time=start_time)
    # reset the HTTP total time
    requests_lib.reset_time_for_thread()

    #
    engine = engines[engine_name]

    # suppose everything will be alright
    requests_exception = False

    try:
        # send requests and parse the results
        search_results = search_one_http_request(engine, query, request_params)

        # check if the engine accepted the request
        if search_results is not None:
            # yes, so add results
            result_container.extend(engine_name, search_results)

            # update engine time when there is no exception
            engine_time = time() - start_time
            page_load_time = requests_lib.get_time_for_thread()
            result_container.add_timing(engine_name, engine_time, page_load_time)
            with threading.RLock():
                engine.stats['engine_time'] += engine_time
                engine.stats['engine_time_count'] += 1
                # update stats with the total HTTP time
                engine.stats['page_load_time'] += page_load_time
                engine.stats['page_load_count'] += 1

    except Exception as e:
        # Timing
        engine_time = time() - start_time
        page_load_time = requests_lib.get_time_for_thread()
        result_container.add_timing(engine_name, engine_time, page_load_time)

        # Record the errors
        with threading.RLock():
            engine.stats['errors'] += 1

        if (issubclass(e.__class__, requests.exceptions.Timeout)):
            result_container.add_unresponsive_engine((engine_name, gettext('timeout')))
            # requests timeout (connect or read)
            logger.error("engine {0} : HTTP requests timeout"
                         "(search duration : {1} s, timeout: {2} s) : {3}"
                         .format(engine_name, engine_time, timeout_limit, e.__class__.__name__))
            requests_exception = True
        elif (issubclass(e.__class__, requests.exceptions.RequestException)):
            result_container.add_unresponsive_engine((engine_name, gettext('request exception')))
            # other requests exception
            logger.exception("engine {0} : requests exception"
                             "(search duration : {1} s, timeout: {2} s) : {3}"
                             .format(engine_name, engine_time, timeout_limit, e))
            requests_exception = True
        else:
            result_container.add_unresponsive_engine((
                engine_name,
                u'{0}: {1}'.format(gettext('unexpected crash'), e),
            ))
            # others errors
            logger.exception('engine {0} : exception : {1}'.format(engine_name, e))

    # suspend or not the engine if there are HTTP errors
    with threading.RLock():
        if requests_exception:
            # update continuous_errors / suspend_end_time
            engine.continuous_errors += 1
            engine.suspend_end_time = time() + min(settings['search']['max_ban_time_on_fail'],
                                                   engine.continuous_errors * settings['search']['ban_time_on_fail'])
        else:
            # no HTTP error (perhaps an engine error)
            # anyway, reset the suspend variables
            engine.continuous_errors = 0
            engine.suspend_end_time = 0