    def new_load_metric_vars(metric_vars_file):
        """
        Load the metric variables for a check from a metric check variables file

        :param metric_vars_file: the path and filename to the metric variables files
        :type metric_vars_file: str
        :return: the metric_vars module object or ``False``
        :rtype: list

        """
        metric_vars = False
        metric_vars_got = False
        if os.path.isfile(metric_vars_file):
            logger.info(
                'loading metric variables from metric_check_file - %s' % (
                    str(metric_vars_file)))

            metric_vars = []
            with open(metric_vars_file) as f:
                for line in f:
                    add_line = line.replace('\n', '')
                    metric_vars.append(add_line)

            # Bug #1460: panorama check file fails
            with open(metric_vars_file) as f:
                try:
                    metric_vars = imp.load_source('metric_vars', '', f)
                    metric_vars_got = True
                except:
                    current_logger.info(traceback.format_exc())
                    msg = 'failed to import metric variables - metric_check_file'
                    current_logger.error(
                        'error :: %s - %s' % (msg, str(metric_vars_file)))
                    metric_vars = False

            if settings.ENABLE_DEBUG and metric_vars_got:
                current_logger.info(
                    'metric_vars determined - metric variable - metric - %s' % str(metric_vars.metric))
        else:
            current_logger.error('error :: metric_vars_file not found - %s' % (str(metric_vars_file)))

        return metric_vars