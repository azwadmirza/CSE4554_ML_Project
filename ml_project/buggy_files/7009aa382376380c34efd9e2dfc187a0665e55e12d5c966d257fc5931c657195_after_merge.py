    def spin_process(self, i, metric_check_file):
        """
        Assign a metric anomaly to process.

        :param i: python process id
        :param metric_check_file: full path to the metric check file

        :return: returns True

        """

        child_process_pid = os.getpid()
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: child_process_pid - %s' % str(child_process_pid))

        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: processing metric check - %s' % metric_check_file)

        if not os.path.isfile(str(metric_check_file)):
            logger.error('error :: file not found - metric_check_file - %s' % (str(metric_check_file)))
            return

        check_file_name = os.path.basename(str(metric_check_file))
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: check_file_name - %s' % check_file_name)
        check_file_timestamp = check_file_name.split('.', 1)[0]
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: check_file_timestamp - %s' % str(check_file_timestamp))
        check_file_metricname_txt = check_file_name.split('.', 1)[1]
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: check_file_metricname_txt - %s' % check_file_metricname_txt)
        check_file_metricname = check_file_metricname_txt.replace('.txt', '')
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: check_file_metricname - %s' % check_file_metricname)
        check_file_metricname_dir = check_file_metricname.replace('.', '/')
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: check_file_metricname_dir - %s' % check_file_metricname_dir)

        metric_failed_check_dir = '%s/%s/%s' % (failed_checks_dir, check_file_metricname_dir, check_file_timestamp)

        failed_check_file = '%s/%s' % (metric_failed_check_dir, check_file_name)
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: failed_check_file - %s' % failed_check_file)

        # Load and validate metric variables
        try:
            # @modified 20170101 - Feature #1830: Ionosphere alerts
            #                      Bug #1460: panorama check file fails
            #                      Panorama check file fails #24
            # Get rid of the skyline_functions imp as imp is deprecated in py3 anyway
            # Use def new_load_metric_vars(self, metric_vars_file):
            # metric_vars = load_metric_vars(skyline_app, str(metric_check_file))
            metric_vars_array = self.new_load_metric_vars(str(metric_check_file))
        except:
            logger.info(traceback.format_exc())
            logger.error('error :: failed to load metric variables from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        # Test metric variables
        # We use a pythonic methodology to test if the variables are defined,
        # this ensures that if any of the variables are not set for some reason
        # we can handle unexpected data or situations gracefully and try and
        # ensure that the process does not hang.
        metric = None
        try:
            # metric_vars.metric
            # metric = str(metric_vars.metric)
            key = 'metric'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            metric = str(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - metric - %s' % metric)
        except:
            logger.error('error :: failed to read metric variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not metric:
            logger.error('error :: failed to load metric variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        value = None
        try:
            # metric_vars.value
            # value = str(metric_vars.value)
            key = 'value'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            value = float(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - value - %s' % (value))
        except:
            logger.error('error :: failed to read value variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not value:
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        from_timestamp = None
        try:
            # metric_vars.from_timestamp
            # from_timestamp = str(metric_vars.from_timestamp)
            key = 'from_timestamp'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            from_timestamp = int(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - from_timestamp - %s' % from_timestamp)
        except:
            # @added 20160822 - Bug #1460: panorama check file fails
            # Added exception handling here
            logger.info(traceback.format_exc())
            logger.error('error :: failed to read from_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not from_timestamp:
            logger.error('error :: failed to load from_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        metric_timestamp = None
        try:
            # metric_vars.metric_timestamp
            # metric_timestamp = str(metric_vars.metric_timestamp)
            key = 'metric_timestamp'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            metric_timestamp = int(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - metric_timestamp - %s' % metric_timestamp)
        except:
            logger.error('error :: failed to read metric_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not metric_timestamp:
            logger.error('error :: failed to load metric_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        algorithms = None
        try:
            # metric_vars.algorithms
            # algorithms = metric_vars.algorithms
            key = 'algorithms'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            algorithms = value_list[0]
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - algorithms - %s' % str(algorithms))
        except:
            logger.error('error :: failed to read algorithms variable from check file setting to all - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not algorithms:
            logger.error('error :: failed to load algorithms variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        triggered_algorithms = None
        try:
            # metric_vars.triggered_algorithms
            # triggered_algorithms = metric_vars.triggered_algorithms
            key = 'triggered_algorithms'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            triggered_algorithms = value_list[0]
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - triggered_algorithms - %s' % str(triggered_algorithms))
        except:
            logger.error('error :: failed to read triggered_algorithms variable from check file setting to all - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not triggered_algorithms:
            logger.error('error :: failed to load triggered_algorithms variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        app = None
        try:
            # metric_vars.app
            # app = str(metric_vars.app)
            key = 'app'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            app = str(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - app - %s' % app)
        except:
            logger.error('error :: failed to read app variable from check file setting to all  - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not app:
            logger.error('error :: failed to load app variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        source = None
        try:
            # metric_vars.source
            # source = str(metric_vars.source)
            key = 'source'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            source = str(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - source - %s' % source)
        except:
            logger.error('error :: failed to read source variable from check file setting to all  - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not app:
            logger.error('error :: failed to load app variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        added_by = None
        try:
            # metric_vars.added_by
            # added_by = str(metric_vars.added_by)
            key = 'added_by'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            added_by = str(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - added_by - %s' % added_by)
        except:
            logger.error('error :: failed to read added_by variable from check file setting to all - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not added_by:
            logger.error('error :: failed to load added_by variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        added_at = None
        try:
            # metric_vars.added_at
            # added_at = str(metric_vars.added_at)
            key = 'added_at'
            value_list = [var_array[1] for var_array in metric_vars_array if var_array[0] == key]
            added_at = str(value_list[0])
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: metric variable - added_at - %s' % added_at)
        except:
            logger.error('error :: failed to read added_at variable from check file setting to all - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        if not added_at:
            logger.error('error :: failed to load added_at variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        record_anomaly = True
        cache_key = '%s.last_check.%s.%s' % (skyline_app, app, metric)
        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: cache_key - %s.last_check.%s.%s' % (
                skyline_app, app, metric))
        try:
            last_check = self.redis_conn.get(cache_key)
        except Exception as e:
            logger.error(
                'error :: could not query cache_key - %s.last_check.%s.%s - %s' % (
                    skyline_app, app, metric, e))
            last_check = None

        if last_check:
            record_anomaly = False
            logger.info(
                'Panorama metric key not expired - %s.last_check.%s.%s' % (
                    skyline_app, app, metric))

        # @added 20160907 - Handle Panorama stampede on restart after not running #26
        # Allow to expire check if greater than PANORAMA_CHECK_MAX_AGE
        if max_age:
            now = time()
            anomaly_age = int(now) - int(metric_timestamp)
            if anomaly_age > max_age_seconds:
                record_anomaly = False
                logger.info(
                    'Panorama check max age exceeded - %s - %s seconds old, older than %s seconds discarding' % (
                        metric, str(anomaly_age), str(max_age_seconds)))

        if not record_anomaly:
            logger.info('not recording anomaly for - %s' % (metric))
            if os.path.isfile(str(metric_check_file)):
                try:
                    os.remove(str(metric_check_file))
                    logger.info('metric_check_file removed - %s' % str(metric_check_file))
                except OSError:
                    pass

            return

        # Determine id of something thing
        def determine_id(table, key, value):
            """
            Get the id of something from Redis or the database and insert a new
            record if one does not exist for the value.

            :param table: table name
            :param key: key name
            :param value: value name
            :type table: str
            :type key: str
            :type value: str
            :return: int or boolean

            """

            query_cache_key = '%s.mysql_ids.%s.%s.%s' % (skyline_app, table, key, value)
            determined_id = None
            redis_determined_id = None
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: query_cache_key - %s' % (query_cache_key))

            try:
                redis_known_id = self.redis_conn.get(query_cache_key)
            except:
                redis_known_id = None

            if redis_known_id:
                unpacker = Unpacker(use_list=False)
                unpacker.feed(redis_known_id)
                redis_determined_id = list(unpacker)

            if redis_determined_id:
                determined_id = int(redis_determined_id[0])

            if determined_id:
                if determined_id > 0:
                    return determined_id

            # Query MySQL
            query = 'select id FROM %s WHERE %s=\'%s\'' % (table, key, value)
            results = self.mysql_select(query)

            determined_id = 0
            if results:
                determined_id = int(results[0][0])

            if determined_id > 0:
                # Set the key for a week
                if not redis_determined_id:
                    try:
                        self.redis_conn.setex(query_cache_key, 604800, packb(determined_id))
                        logger.info('set redis query_cache_key - %s - id: %s' % (
                            query_cache_key, str(determined_id)))
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error('error :: failed to set query_cache_key - %s - id: %s' % (
                            query_cache_key, str(determined_id)))
                return int(determined_id)

            # INSERT because no known id
            insert_query = 'insert into %s (%s) VALUES (\'%s\')' % (table, key, value)
            logger.info('inserting %s into %s table' % (value, table))
            try:
                results = self.mysql_insert(insert_query)
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: failed to determine the id of %s from the insert' % (value))
                raise

            determined_id = 0
            if results:
                determined_id = int(results)
            else:
                logger.error('error :: results not set')
                raise

            if determined_id > 0:
                # Set the key for a week
                if not redis_determined_id:
                    try:
                        self.redis_conn.setex(query_cache_key, 604800, packb(determined_id))
                        logger.info('set redis query_cache_key - %s - id: %s' % (
                            query_cache_key, str(determined_id)))
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error('%s' % str(e))
                        logger.error('error :: failed to set query_cache_key - %s - id: %s' % (
                            query_cache_key, str(determined_id)))
                return determined_id

            logger.error('error :: failed to determine the inserted id for %s' % value)
            return False

        try:
            added_by_host_id = determine_id('hosts', 'host', added_by)
        except:
            logger.error('error :: failed to determine id of %s' % (added_by))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            app_id = determine_id('apps', 'app', app)
        except:
            logger.error('error :: failed to determine id of %s' % (app))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            source_id = determine_id('sources', 'source', source)
        except:
            logger.error('error :: failed to determine id of %s' % (source))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            metric_id = determine_id('metrics', 'metric', metric)
        except:
            logger.error('error :: failed to determine id of %s' % (metric))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        algorithms_ids_csv = ''
        for algorithm in algorithms:
            try:
                algorithm_id = determine_id('algorithms', 'algorithm', algorithm)
            except:
                logger.error('error :: failed to determine id of %s' % (algorithm))
                fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
                return False
            if algorithms_ids_csv == '':
                algorithms_ids_csv = str(algorithm_id)
            else:
                new_algorithms_ids_csv = '%s,%s' % (algorithms_ids_csv, str(algorithm_id))
                algorithms_ids_csv = new_algorithms_ids_csv

        triggered_algorithms_ids_csv = ''
        for triggered_algorithm in triggered_algorithms:
            try:
                triggered_algorithm_id = determine_id('algorithms', 'algorithm', triggered_algorithm)
            except:
                logger.error('error :: failed to determine id of %s' % (triggered_algorithm))
                fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
                return False
            if triggered_algorithms_ids_csv == '':
                triggered_algorithms_ids_csv = str(triggered_algorithm_id)
            else:
                new_triggered_algorithms_ids_csv = '%s,%s' % (
                    triggered_algorithms_ids_csv, str(triggered_algorithm_id))
                triggered_algorithms_ids_csv = new_triggered_algorithms_ids_csv

        logger.info('inserting anomaly')
        try:
            full_duration = int(metric_timestamp) - int(from_timestamp)
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: full_duration - %s' % str(full_duration))
        except:
            logger.error('error :: failed to determine full_duration')
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            anomalous_datapoint = round(float(value), 6)
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: anomalous_datapoint - %s' % str(anomalous_datapoint))
        except:
            logger.error('error :: failed to determine anomalous_datapoint')
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            columns = '%s, %s, %s, %s, %s, %s, %s, %s, %s' % (
                'metric_id', 'host_id', 'app_id', 'source_id',
                'anomaly_timestamp', 'anomalous_datapoint', 'full_duration',
                'algorithms_run', 'triggered_algorithms')
            if settings.ENABLE_PANORAMA_DEBUG:
                logger.info('debug :: columns - %s' % str(columns))
        except:
            logger.error('error :: failed to construct columns string')
            logger.info(traceback.format_exc())
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        try:
            query = 'insert into anomalies (%s) VALUES (%d, %d, %d, %d, %s, %.6f, %d, \'%s\', \'%s\')' % (
                columns, metric_id, added_by_host_id, app_id, source_id,
                metric_timestamp, anomalous_datapoint, full_duration,
                algorithms_ids_csv, triggered_algorithms_ids_csv)
        except:
            logger.error('error :: failed to construct insert query')
            logger.info(traceback.format_exc())
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        if settings.ENABLE_PANORAMA_DEBUG:
            logger.info('debug :: anomaly insert - %s' % str(query))

        try:
            anomaly_id = self.mysql_insert(query)
            logger.info('anomaly id - %d - created for %s at %s' % (
                anomaly_id, metric, metric_timestamp))
        except:
            logger.error('error :: failed to insert anomaly %s at %s' % (
                anomaly_id, metric, metric_timestamp))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return False

        # Set anomaly record cache key
        try:
            self.redis_conn.setex(
                cache_key, settings.PANORAMA_EXPIRY_TIME, packb(value))
            logger.info('set cache_key - %s.last_check.%s.%s - %s' % (
                skyline_app, app, metric, str(settings.PANORAMA_EXPIRY_TIME)))
        except Exception as e:
            logger.error(
                'error :: could not query cache_key - %s.last_check.%s.%s - %s' % (
                    skyline_app, app, metric, e))

        if os.path.isfile(str(metric_check_file)):
            try:
                os.remove(str(metric_check_file))
                logger.info('metric_check_file removed - %s' % str(metric_check_file))
            except OSError:
                pass

        return anomaly_id