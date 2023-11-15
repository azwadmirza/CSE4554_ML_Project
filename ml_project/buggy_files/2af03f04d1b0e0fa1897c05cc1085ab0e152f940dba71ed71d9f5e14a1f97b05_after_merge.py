    def _store_logs(self, func_details, log_output, invocation_time):
        if not aws_stack.is_service_enabled('logs'):
            return
        logs_client = aws_stack.connect_to_service('logs')
        log_group_name = '/aws/lambda/%s' % func_details.name()
        time_str = time.strftime('%Y/%m/%d', time.gmtime(invocation_time))
        log_stream_name = '%s/[$LATEST]%s' % (time_str, short_uid())

        # make sure that the log group exists
        log_groups = logs_client.describe_log_groups()['logGroups']
        log_groups = [lg['logGroupName'] for lg in log_groups]
        if log_group_name not in log_groups:
            try:
                logs_client.create_log_group(logGroupName=log_group_name)
            except botocore.errorfactory.ResourceAlreadyExistsException:
                # this can happen in certain cases, possibly due to a race condition
                pass

        # create a new log stream for this lambda invocation
        logs_client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

        # store new log events under the log stream
        invocation_time = invocation_time
        finish_time = int(time.time() * 1000)
        log_lines = log_output.split('\n')
        time_diff_per_line = float(finish_time - invocation_time) / float(len(log_lines))
        log_events = []
        for i, line in enumerate(log_lines):
            if not line:
                continue
            # simple heuristic: assume log lines were emitted in regular intervals
            log_time = invocation_time + float(i) * time_diff_per_line
            event = {'timestamp': int(log_time), 'message': line}
            log_events.append(event)
        if not log_events:
            return
        logs_client.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=log_events
        )