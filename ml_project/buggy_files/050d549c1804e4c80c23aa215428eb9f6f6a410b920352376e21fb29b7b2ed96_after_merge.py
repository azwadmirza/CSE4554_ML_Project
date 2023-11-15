def search_one_offline_request_safe(engine_name, query, request_params, result_container, start_time, timeout_limit):
    engine = engines[engine_name]

    try:
        search_results = search_one_offline_request(engine, query, request_params)

        if search_results:
            result_container.extend(engine_name, search_results)

            engine_time = time() - start_time
            result_container.add_timing(engine_name, engine_time, engine_time)
            with threading.RLock():
                engine.stats['engine_time'] += engine_time
                engine.stats['engine_time_count'] += 1

    except ValueError as e:
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        logger.exception('engine {0} : invalid input : {1}'.format(engine_name, e))
    except Exception as e:
        record_offline_engine_stats_on_error(engine, result_container, start_time)
        result_container.add_unresponsive_engine(engine_name, 'unexpected crash', str(e))
        logger.exception('engine {0} : exception : {1}'.format(engine_name, e))