    def spin_process(self, i, metric_check_file):
        """
        Assign a metric anomaly to process.

        :param i: python process id
        :param metric_check_file: full path to the metric check file

        :return: returns True

        """

        def get_an_engine():
            try:
                engine, log_msg, trace = get_engine(skyline_app)
                return engine, log_msg, trace
            except:
                logger.error(traceback.format_exc())
                log_msg = 'error :: failed to get MySQL engine in spin_process'
                logger.error('error :: failed to get MySQL engine in spin_process')
                return None, log_msg, trace

        child_process_pid = os.getpid()
        logger.info('child_process_pid - %s' % str(child_process_pid))

        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: processing metric check - %s' % metric_check_file)

        if not os.path.isfile(str(metric_check_file)):
            logger.error('error :: file not found - metric_check_file - %s' % (str(metric_check_file)))
            return

        check_file_name = os.path.basename(str(metric_check_file))
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: check_file_name - %s' % check_file_name)
        check_file_timestamp = check_file_name.split('.', 1)[0]
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: check_file_timestamp - %s' % str(check_file_timestamp))
        check_file_metricname_txt = check_file_name.split('.', 1)[1]
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: check_file_metricname_txt - %s' % check_file_metricname_txt)
        check_file_metricname = check_file_metricname_txt.replace('.txt', '')
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: check_file_metricname - %s' % check_file_metricname)
        check_file_metricname_dir = check_file_metricname.replace('.', '/')
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: check_file_metricname_dir - %s' % check_file_metricname_dir)

        metric_failed_check_dir = '%s/%s/%s' % (failed_checks_dir, check_file_metricname_dir, check_file_timestamp)

        failed_check_file = '%s/%s' % (metric_failed_check_dir, check_file_name)
        if settings.ENABLE_IONOSPHERE_DEBUG:
            logger.info('debug :: failed_check_file - %s' % failed_check_file)

        # Load and validate metric variables
        current_metrics_var = None
        try:
            metric_vars = load_metric_vars(skyline_app, str(metric_check_file))
            # @added 20161230 - Panorama check file fails #24
            # Could this do it
            current_metrics_var = metric_vars
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
        try:
            metric_vars.metric
            metric = str(metric_vars.metric)
            base_name = metric
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - metric - %s' % metric)
        except:
            logger.error('error :: failed to read metric variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        try:
            metric_vars.value
            value = str(metric_vars.value)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - value - %s' % (value))
        except:
            logger.error('error :: failed to read value variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        try:
            metric_vars.from_timestamp
            from_timestamp = str(metric_vars.from_timestamp)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - from_timestamp - %s' % from_timestamp)
        except:
            # @added 20160822 - Bug #1460: panorama check file fails
            # Added exception handling here
            logger.info(traceback.format_exc())
            logger.error('error :: failed to read from_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        try:
            metric_vars.metric_timestamp
            metric_timestamp = str(metric_vars.metric_timestamp)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - metric_timestamp - %s' % metric_timestamp)
        except:
            logger.error('error :: failed to read metric_timestamp variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        try:
            metric_vars.algorithms
            algorithms = metric_vars.algorithms
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - algorithms - %s' % str(algorithms))
        except:
            logger.error('error :: failed to read algorithms variable from check file setting to all - %s' % (metric_check_file))
            algorithms = 'all'

        try:
            metric_vars.triggered_algorithms
            triggered_algorithms = metric_vars.triggered_algorithms
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - triggered_algorithms - %s' % str(triggered_algorithms))
        except:
            logger.error('error :: failed to read triggered_algorithms variable from check file setting to all - %s' % (metric_check_file))
            triggered_algorithms = 'all'

        try:
            metric_vars.added_by
            added_by = str(metric_vars.added_by)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - added_by - %s' % added_by)
        except:
            logger.error('error :: failed to read added_by variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        try:
            metric_vars.added_at
            added_at = str(metric_vars.added_at)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - added_at - %s' % added_at)
        except:
            logger.error('error :: failed to read added_at variable from check file setting to all - %s' % (metric_check_file))
            added_by = 'all'

        # @added 20161228 - Feature #1828: ionosphere - mirage Redis data features
        # Added full_duration which needs to be recorded to allow Mirage metrics
        # to be profiled on Redis timeseries data at FULL_DURATION
        try:
            metric_vars.full_duration
            full_duration = str(metric_vars.full_duration)
            if settings.ENABLE_IONOSPHERE_DEBUG:
                logger.info('debug :: metric variable - full_duration - %s' % full_duration)
        except:
            logger.error('error :: failed to read full_duration variable from check file - %s' % (metric_check_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        now = time()
        anomaly_age = int(now) - int(metric_timestamp)
        if anomaly_age > max_age_seconds:
            logger.info(
                'Ionosphere check max age exceeded - %s - %s seconds old, older than %s seconds discarding' % (
                    metric, str(anomaly_age), str(max_age_seconds)))
            with open(metric_check_file, 'rt') as fr:
                metric_check_file_contents = fr.readlines()
                logger.info(
                    'debug :: metric check file contents\n%s' % (str(metric_check_file_contents)))
                self.remove_metric_check_file(str(metric_check_file))
                return

        # @added 20161222 - ionosphere should extract features for every anomaly
        # check that is sent through and calculate a feature_profile ready for
        # submission by the user if they so choose.  Further ionosphere could
        # make itself more useful by comparing any training data profiles to
        # further anomalies, however the feature profiles for subsequent
        # anomalies may be similar enough to match a few times and each a closer
        # match to the next.
        training_metric = False

        # Check if the metric has ionosphere_enabled, if not remove the check
        # file but not the data directory
        # @modified 20161230 - Feature #1830: Ionosphere alerts
        # Use SQLAlchemy method
        # query = "SELECT ionosphere_enabled FROM metrics WHERE metric='%s'" % metric
        # result = mysql_select(skyline_app, query)
        # if str(result[0]) != '1':
        #     logger.info('Ionosphere not enabled on %s' % (metric))
        #     # @modified 20161222 - do not remove metric file until features
        #     # calculated
        #     # self.remove_metric_check_file(str(metric_check_file))
        #     # return
        #     training_metric = True
        try:
            engine, log_msg, trace = get_an_engine()
            logger.info(log_msg)
        except:
            logger.error(traceback.format_exc())
            logger.error('error :: could not get a MySQL engine to determine ionosphere_enabled')

        if not engine:
            logger.error('error :: engine not obtained to determine ionosphere_enabled')

        # Get the metrics_table metadata
        metrics_table = None
        try:
            metrics_table, log_msg, trace = metrics_table_meta(skyline_app, engine)
            logger.info('metrics_table OK for %s' % base_name)
        except:
            logger.error(traceback.format_exc())
            logger.error('error :: failed to get metrics_table meta for %s' % base_name)

        metrics_id = None
        metric_ionosphere_enabled = None
        try:
            connection = engine.connect()
            # stmt = select([metrics_table.c.ionosphere_enabled]).where(metrics_table.c.metric == str(metric))
            stmt = select([metrics_table]).where(metrics_table.c.metric == base_name)
            result = connection.execute(stmt)
            row = result.fetchone()
            metrics_id = row['id']
            metric_ionosphere_enabled = row['ionosphere_enabled']
            connection.close()

            if metric_ionosphere_enabled is not None:
                training_metric = False
            else:
                # @modified 20161222 - do not remove metric file until features
                # calculated
                # self.remove_metric_check_file(str(metric_check_file))
                # return
                training_metric = True
        except:
            logger.error(traceback.format_exc())
            logger.error('error :: could not determine ionosphere_enabled from metrics table for - %s' % base_name)
            metric_ionosphere_enabled = None
            training_metric = True

        logger.info(
            'ionosphere_enabled is %s for metric id %s - %s' % (
                str(metric_ionosphere_enabled), str(metrics_id),
                base_name))

        if training_metric:
            logger.info('Ionosphere is not enabled on %s' % (base_name))
        else:
            logger.info('Ionosphere is enabled on %s' % (base_name))

        # @added 20161210 - Branch #922: ionosphere
        #                   Task #1658: Patterning Skyline Ionosphere
        # Only continue if there is a training data json timeseries file
        metric_timeseries_dir = base_name.replace('.', '/')
        metric_training_data_dir = '%s/%s/%s' % (
            settings.IONOSPHERE_DATA_FOLDER, metric_timestamp,
            metric_timeseries_dir)
        anomaly_json = '%s/%s.json' % (metric_training_data_dir, base_name)
        if os.path.isfile(anomaly_json):
            logger.info('training data ts json available - %s' % (anomaly_json))
        else:
            logger.error('error :: training data ts json was not found - %s' % (anomaly_json))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        # @added 20161228 - Feature #1828: ionosphere - mirage Redis data features
        # The timeseries full_duration needs to be recorded to allow Mirage metrics to
        # be profiled on Redis timeseries data at FULL_DURATION
        # e.g. mirage.redis.24h.json
        if training_metric:
            logger.info('training metric - %s' % (base_name))

        if added_by == 'mirage':
            logger.info('checking training data Redis json is available')
            # Always calculate features for both the SECOND_ORDER_RESOLUTION_SECONDS
            # timeseries data and the FULL_DURATION Redis timeseries data.
            # It is always preferable to create a features profile on a FULL_DURATION
            # data set, unless the user is flagging the actual Mirage timeseries as
            # not anomalous.  In the Mirage context the not anomalous may often be more
            # "visibile" in the FULL_DURATION view and if so should be matched on the
            # FULL_DURATION timeseries data, even if it is a Mirage metric.
            # Features profiles can be created for a Mirage metric on both the
            # FULL_DURATION and the SECOND_ORDER_RESOLUTION_SECONDS data sets, however
            # only one should be needed.
            # A features profile should always be created at the highest resolution
            # possible, FULL_DURATION data, wherever possible.
            try:
                full_duration_hours = str(int(settings.FULL_DURATION / 3600))
                redis_anomaly_json = '%s/%s.mirage.redis.%sh.json' % (metric_training_data_dir, base_name, full_duration_hours)
                if os.path.isfile(redis_anomaly_json):
                    logger.info('training data Redis full duration ts json available - %s' % (redis_anomaly_json))
                else:
                    logger.error('error :: training data Redis full duration json was not found - %s' % (redis_anomaly_json))
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: training data Redis full duration json was not found - %s' % (redis_anomaly_json))

        # @added 20161209 - Branch #922: ionosphere
        #                   Task #1658: Patterning Skyline Ionosphere
        # Use SQLAlchemy, mysql.connector is still upstairs ^^ but starting the
        # move to SQLAlchemy now that all the webapp Ionosphere SQLAlchemy
        # patterns work and the database lay out if defined we can begin on the
        # data side.  Ionosphere was put together backwards, like tsfresh was
        # learnt.  It was the people input first here in many ways, which is
        # exactly how it was suppose to be.
        # This is now the Ionosphere meat.
        # Get a MySQL engine only if not training_metric
        if not training_metric:

            if not metrics_id:
                logger.error('error :: metric id not known')
                fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
                return False

            logger.info('getting MySQL engine')
            try:
                engine, log_msg, trace = get_an_engine()
                logger.info(log_msg)
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: could not get a MySQL engine to get fp_ids')

            if not engine:
                logger.error('error :: engine not obtained to get fp_ids')

            try:
                ionosphere_table, log_msg, trace = ionosphere_table_meta(skyline_app, engine)
                logger.info(log_msg)
                logger.info('ionosphere_table OK')
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: failed to get ionosphere_table meta for %s' % base_name)

            # Determine the fp_ids that exist for the metric
            fp_ids = []
            fp_ids_found = False
            try:
                connection = engine.connect()
                stmt = select([ionosphere_table]).where(ionosphere_table.c.metric_id == metrics_id)
                result = connection.execute(stmt)
                for row in result:
                    if int(row['full_duration']) == int(full_duration):
                        fp_id = row['id']
                        fp_ids.append(int(fp_id))
                        logger.info('using fp id %s matched full_duration %s - %s' % (str(fp_id), str(full_duration), base_name))
                else:
                        logger.info('not using fp id %s not matched full_duration %s - %s' % (str(fp_id), str(full_duration), base_name))
                connection.close()
                fp_count = len(fp_ids)
                logger.info('determined %s fp ids for %s' % (str(fp_count), base_name))
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: could not determine fp ids from DB for %s' % base_name)
                fp_count = 0

            if len(fp_ids) == 0:
                logger.error('error :: there are no fp ids for %s' % base_name)
            else:
                fp_ids_found = True

        # @added 20161221 - TODO: why not calculate the features of every
        # anomaly so the the use does not have to do it and wait for the
        # features to be calculated.
        # Check the features were calculated by the webapp
        calculated_feature_file = '%s/%s.tsfresh.input.csv.features.transposed.csv' % (metric_training_data_dir, base_name)
        calculated_feature_file_found = False
        if os.path.isfile(calculated_feature_file):
            logger.info('calculated features available - %s' % (calculated_feature_file))
            calculated_feature_file_found = True

        if not calculated_feature_file_found:
            if training_metric:
                # Allow Graphite resources to be created if they are not an alert
                # was not sent therefore features do not need to be calculated
                check_time = int(time())
                check_age = check_time - int(added_at)
                if check_age < 5:
                    sleep(5)
                graphite_file_count = len([f for f in os.listdir(metric_training_data_dir)
                                           if f.endswith('.png') and
                                           os.path.isfile(os.path.join(metric_training_data_dir, f))])
                if graphite_file_count == 0:
                    logger.info('not calculating features no anomaly Graphite alert resources created in %s' % (metric_training_data_dir))
                    self.remove_metric_check_file(str(metric_check_file))
                    return
                else:
                    logger.info('anomaly Graphite alert resources found in %s' % (metric_training_data_dir))

        context = skyline_app
        f_calc = None
        if not calculated_feature_file_found:
            try:
                fp_csv, successful, fp_exists, fp_id, log_msg, traceback_format_exc, f_calc = calculate_features_profile(skyline_app, metric_timestamp, base_name, context)
            except:
                logger.error(traceback.format_exc())
                logger.error('error :: failed to calculate features')
                fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
                return

        if os.path.isfile(calculated_feature_file):
            logger.info('calculated features available - %s' % (calculated_feature_file))
            calculated_feature_file_found = True
            if isinstance(f_calc, float):
                f_calc_time = '%.2f' % f_calc
                send_metric_name = '%s.features_calculation_time' % skyline_app_graphite_namespace
                send_graphite_metric(skyline_app, send_metric_name, f_calc_time)
            if training_metric:
                logger.info('training metric done')
                self.remove_metric_check_file(str(metric_check_file))
                # TODO: make ionosphere more useful, compare any other
                # available training_metric profiles here and match, not in the
                # db context, in the training context.
                return

        # @added 20161210 - Branch #922: ionosphere
        #                   Task #1658: Patterning Skyline Ionosphere
        # Calculate features for the current timeseries if there are fp ids
        # Just call it via the webapp... fewer lines of code and already done in
        # webapp/ionosphere_backend.py and webapp/features_proifle.py
        if not calculated_feature_file_found:
            webapp_url = '%s/ionosphere?timestamp=%s&metric=%s&calc_features=true' % (
                settings.SKYLINE_URL, metric_timestamp, base_name)
            r = None
            http_status_code = 0
            if settings.WEBAPP_AUTH_ENABLED:
                # 10 second timout is sufficient locally under normal circumstances
                # as tsfresh has yet to have been take longer than 6 seconds if so
                # by the time the next request is made, the features file should
                # exist.  So this is limited psuedo-idempotency.
                timeout_and_auth = 'timeout=10, auth=(%s, %s))' % (settings.WEBAPP_AUTH_USER, settings.WEBAPP_AUTH_USER_PASSWORD)
            else:
                timeout_and_auth = 'timeout=10'
            if fp_ids_found:
                for _ in range(2):
                    try:
                        r = requests.get(webapp_url, timeout_and_auth)
                        http_status_code = r.status_code
                    except:
                        logger.error('error :: could not retrieve %s' % webapp_url)
                        sleep(5)
                        continue
                    else:
                        break
                else:
                    logger.error(traceback.format_exc())
                    logger.error('error :: could not retrieve %s after 3 tries' % webapp_url)

            if int(http_status_code) == 200:
                if os.path.isfile(calculated_feature_file):
                    logger.info('calculated features available - %s' % (calculated_feature_file))
                    calculated_feature_file_found = True
                else:
                    logger.error('error :: calculated features not available - %s' % (calculated_feature_file))
                    # send an Ionosphere alert or add a thunder branch alert, one
                    # one thing at a time.  You cannot rush timeseries.
                    self.remove_metric_check_file(str(metric_check_file))
                    return

        # @modified 20161213 - Branch #1790: test_tsfresh
        # TODO: Match the test_tsfresh method
        # Create an array of the calculated features
        calculated_features = []
        if calculated_feature_file_found:
            count_id = 0
            with open(calculated_feature_file, 'rb') as fr:
                reader = csv.reader(fr, delimiter=',')
                for i, line in enumerate(reader):
                    if str(line[0]) != '':
                        if ',' in line[0]:
                            feature_name = '"%s"' % str(line[0])
                        else:
                            feature_name = str(line[0])
                        count_id += 1
                        value = float(line[1])
                        calculated_features.append([feature_name, value])

        if len(calculated_features) == 0:
            logger.error('error :: no calculated features were determined from - %s' % (calculated_feature_file))
            fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
            return

        # Compare calculated features to feature values for each fp id
        not_anomalous = False
        if calculated_feature_file_found:
            for fp_id in fp_ids:
                if not metrics_id:
                    logger.error('error :: metric id not known')
                    fail_check(skyline_app, metric_failed_check_dir, str(metric_check_file))
                    return False

                features_count = None
                fp_features = []
                # Get features for fp_id from z_fp_<metric_id> table where the
                # features profile is the same full_duration
                metric_fp_table = 'z_fp_%s' % str(metrics_id)
                try:
                    engine, log_msg, trace = get_an_engine()
                except:
                    logger.error(traceback.format_exc())
                    logger.error('error :: could not get a MySQL engine for feature_id and values from %s' % metric_fp_table)

                if not engine:
                    logger.error('error :: engine not obtained for feature_id and values from %s' % metric_fp_table)

                try:
                    stmt = 'SELECT feature_id, value FROM %s WHERE fp_id=%s' % (metric_fp_table, str(fp_id))
                    connection = engine.connect()
                    for row in engine.execute(stmt):
                        fp_feature_id = int(row['feature_id'])
                        fp_value = float(row['value'])
                        fp_features.append([fp_feature_id, fp_value])
                    connection.close()
                    features_count = len(fp_features)
                    logger.info('determined %s features for fp_id %s' % (str(features_count), str(fp_id)))
                except:
                    logger.error(traceback.format_exc())
                    logger.error('error :: could not determine feature_id, value from %s' % metric_fp_table)

                # Convert feature names in calculated_features to their id
                logger.info('converting tsfresh feature names to Skyline feature ids')
                calc_features_by_id = []
                for feature_name, value in calculated_features:
                    for skyline_feature_id, name in TSFRESH_FEATURES:
                        if feature_name == name:
                            calc_features_by_id.append([skyline_feature_id, float(value)])

                # Determine what features each data has, extract only values for
                # common features.
                logger.info('determining common features')
                relevant_fp_feature_values = []
                relevant_calc_feature_values = []
                for skyline_feature_id, value in calc_features_by_id:
                    for fp_feature_id, fp_value in fp_features:
                        if skyline_feature_id == fp_feature_id:
                            relevant_fp_feature_values.append(fp_value)
                            relevant_calc_feature_values.append(value)

                # Determine the sum of each set
                relevant_fp_feature_values_count = len(relevant_fp_feature_values)
                relevant_calc_feature_values_count = len(relevant_calc_feature_values)
                if relevant_fp_feature_values_count != relevant_calc_feature_values_count:
                    logger.error('error :: mismatch in number of common features')
                    logger.error('error :: relevant_fp_feature_values_count - %s' % str(relevant_fp_feature_values_count))
                    logger.error('error :: relevant_calc_feature_values_count - %s' % str(relevant_calc_feature_values_count))
                    continue
                else:
                    logger.info('comparing on %s common features' % str(relevant_fp_feature_values_count))

                if relevant_fp_feature_values_count == 0:
                    logger.error('error :: relevant_fp_feature_values_count is zero')
                    continue

                # Determine the sum of each set
                sum_fp_values = sum(relevant_fp_feature_values)
                sum_calc_values = sum(relevant_calc_feature_values)
                logger.info(
                    'sum of the values of the %s common features in features profile - %s' % (
                        str(relevant_fp_feature_values_count), str(sum_fp_values)))
                logger.info(
                    'sum of the values of the %s common features in the calculated features - %s' % (
                        str(relevant_calc_feature_values_count), str(sum_calc_values)))

                # Determine whether each set is positive or negative
                # # if the same carry on
                # # if both negative, make then both positive
                # Sum fp values, Sum calculated - handle negatives like features_sum :: -3389570699080000.0000000000
                # Determine whether each set is positive or negative
                # # if the same carry on
                # # if both negative, make then both positive postive_sums
                fp_sum_array = [sum_fp_values]
                calc_sum_array = [sum_calc_values]
                almost_equal = None
                try:
                    np.testing.assert_array_almost_equal(fp_sum_array, calc_sum_array)
                    almost_equal = True
                except:
                    almost_equal = False

                if almost_equal:
                    not_anomalous = True
                    logger.info('common features sums are almost equal, not anomalous' % str(relevant_fp_feature_values_count))

                percent_different = 100
                sums_array = np.array([sum_fp_values, sum_calc_values], dtype=float)
                try:
                    calc_percent_different = np.diff(sums_array) / sums_array[:-1] * 100.
                    percent_different = calc_percent_different[0]
                    logger.info('percent_different between common features sums - %s' % str(percent_different))
                except:
                    logger.error(traceback.format_exc())
                    logger.error('error :: failed to calculate percent_different')
                    continue

                # @added 20161229 - Feature #1830: Ionosphere alerts
                # Update the features profile checked count and time
                logger.info('updating checked details in db for %s' % (str(fp_id)))
                # update matched_count in ionosphere_table
                checked_timestamp = int(time())

                try:
                    engine, log_msg, trace = get_an_engine()
                except:
                    logger.error(traceback.format_exc())
                    logger.error('error :: could not get a MySQL engine to update checked details in db for %s' % (str(fp_id)))
                if not engine:
                    logger.error('error :: engine not obtained to update checked details in db for %s' % (str(fp_id)))

                try:
                    connection = engine.connect()
                    connection.execute(
                        ionosphere_table.update(
                            ionosphere_table.c.id == fp_id).
                        values(checked_count=ionosphere_table.c.checked_count + 1,
                               last_checked=checked_timestamp))
                    connection.close()
                    logger.info('updated checked_count for %s' % str(fp_id))
                except:
                    logger.error(traceback.format_exc())
                    logger.error('error :: could not update checked_count and last_checked for %s ' % str(fp_id))

                # if diff_in_sums <= 1%:
                if percent_different < 0:
                    new_pdiff = percent_different * -1
                    percent_different = new_pdiff

                if percent_different < settings.IONOSPHERE_FEATURES_PERCENT_SIMILAR:
                    not_anomalous = True
                    # log
                    logger.info('not anomalous - features profile match - %s' % base_name)
                    logger.info(
                        'calculated features sum are within %s percent of fp_id %s with %s, not anomalous' %
                        (str(settings.IONOSPHERE_FEATURES_PERCENT_SIMILAR),
                            str(fp_id), str(percent_different)))
                    # update matched_count in ionosphere_table
                    matched_timestamp = int(time())
                    try:
                        engine, log_msg, trace = get_an_engine()
                    except:
                        logger.error(traceback.format_exc())
                        logger.error('error :: could not get a MySQL engine to update matched details in db for %s' % (str(fp_id)))
                    if not engine:
                        logger.error('error :: engine not obtained to update matched details in db for %s' % (str(fp_id)))

                    try:
                        connection = engine.connect()
                        connection.execute(
                            ionosphere_table.update(
                                ionosphere_table.c.id == fp_id).
                            values(matched_count=ionosphere_table.c.matched_count + 1,
                                   last_matched=matched_timestamp))
                        connection.close()
                        logger.info('updated matched_count for %s' % str(fp_id))
                    except:
                        logger.error(traceback.format_exc())
                        logger.error('error :: could not update matched_count and last_matched for %s ' % str(fp_id))

                # https://docs.scipy.org/doc/numpy/reference/generated/numpy.testing.assert_almost_equal.html
                # @added 20161214 - Add a between timeframe option, e.g. if
                # fp match, only see this as not anomalous if hour (and or min)
                # is between x and y - handle rollovers, cron log archives, etc.
                logger.info('debug :: %s is a features profile for %s' % (str(fp_id), base_name))

            if not not_anomalous:
                logger.info('anomalous - no feature profiles were matched - %s' % base_name)
                # Send to panorama as Analyzer and Mirage will only alert on the
                # anomaly, they will not push it to Panorama
                if settings.PANORAMA_ENABLED:
                    if not os.path.exists(settings.PANORAMA_CHECK_PATH):
                        mkdir_p(settings.PANORAMA_CHECK_PATH)
                    # Note:
                    # The values are enclosed is single quoted intentionally
                    # as the imp.load_source used results in a shift in the
                    # decimal position when double quoted, e.g.
                    # value = "5622.0" gets imported as
                    # 2016-03-02 12:53:26 :: 28569 :: metric variable - value - 562.2
                    # single quoting results in the desired,
                    # 2016-03-02 13:16:17 :: 1515 :: metric variable - value - 5622.0
                    added_at = str(int(time()))
                    source = 'graphite'
                    panaroma_anomaly_data = 'metric = \'%s\'\n' \
                                            'value = \'%s\'\n' \
                                            'from_timestamp = \'%s\'\n' \
                                            'metric_timestamp = \'%s\'\n' \
                                            'algorithms = %s\n' \
                                            'triggered_algorithms = %s\n' \
                                            'app = \'%s\'\n' \
                                            'source = \'%s\'\n' \
                                            'added_by = \'%s\'\n' \
                                            'added_at = \'%s\'\n' \
                        % (base_name, str(value), from_timestamp,
                           metric_timestamp, str(settings.ALGORITHMS),
                           triggered_algorithms, skyline_app, source,
                           this_host, added_at)

                    # Create an anomaly file with details about the anomaly
                    panaroma_anomaly_file = '%s/%s.%s.txt' % (
                        settings.PANORAMA_CHECK_PATH, added_at,
                        base_name)
                    try:
                        write_data_to_file(
                            skyline_app, panaroma_anomaly_file, 'w',
                            panaroma_anomaly_data)
                        logger.info('added panorama anomaly file :: %s' % (panaroma_anomaly_file))
                        self.sent_to_panorama.append(base_name)

                    except:
                        logger.error('error :: failed to add panorama anomaly file :: %s' % (panaroma_anomaly_file))
                        logger.info(traceback.format_exc())
                else:
                    logger.info('not adding panorama anomaly file for Mirage metric - %s' % (metric))

            #     alert ... hmmm the harder part, maybe not all the resources
            #     are already created, so just determining ALERTS and firing a
            #     trigger_alert (pull in alerter.py and mirage_alerters.py?)
            #     OR send back to app via Redis
                cache_key = 'ionosphere.%s.alert.%s.%s' % (added_by, metric_timestamp, base_name)
                try:
                    self.redis_conn.setex(
                        cache_key, 300,
                        [float(value), base_name, int(metric_timestamp), triggered_algorithms, full_duration])
                    logger.info(
                        'add Redis alert key - %s - [%s, \'%s\', %s, %s]' %
                        (cache_key, str(value), base_name, str(int(metric_timestamp)),
                            str(triggered_algorithms)))
                except:
                    logger.error(traceback.format_exc())
                    logger.error(
                        'error :: failed to add Redis key - %s - [%s, \'%s\', %s, %s]' %
                        (cache_key, str(value), base_name, str(int(metric_timestamp)),
                            str(triggered_algorithms)))

        # TO BE REMOVED
        self.remove_metric_check_file(str(metric_check_file))
        return