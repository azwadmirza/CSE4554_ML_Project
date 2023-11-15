def create_or_update_alarm(
        connection=None, name=None, metric=None, namespace=None,
        statistic=None, comparison=None, threshold=None, period=None,
        evaluation_periods=None, unit=None, description='',
        dimensions=None, alarm_actions=None,
        insufficient_data_actions=None, ok_actions=None,
        region=None, key=None, keyid=None, profile=None):
    '''
    Create or update a cloudwatch alarm.

    Params are the same as:
        http://boto.readthedocs.org/en/latest/ref/cloudwatch.html#boto.ec2.cloudwatch.alarm.MetricAlarm.

    Dimensions must be a dict. If the value of Dimensions is a string, it will
    be json decoded to produce a dict. alarm_actions, insufficient_data_actions,
    and ok_actions must be lists of string.  If the passed-in value is a string,
    it will be split on "," to produce a list. The strings themselves for
    alarm_actions, insufficient_data_actions, and ok_actions must be Amazon
    resource names (ARN's); however, this method also supports an arn lookup
    notation, as follows:

        arn:aws:....                                    ARN as per http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
        scaling_policy:<as_name>:<scaling_policy_name>  The named autoscale group scaling policy, for the named group (e.g.  scaling_policy:my-asg:ScaleDown)

    This is convenient for setting up autoscaling as follows.  First specify a
    boto_asg.present state for an ASG with scaling_policies, and then set up
    boto_cloudwatch_alarm.present states which have alarm_actions that
    reference the scaling_policy.

    CLI example:

        salt myminion boto_cloudwatch.create_alarm name=myalarm ... region=us-east-1
    '''
    # clean up argument types, so that CLI works
    if threshold:
        threshold = float(threshold)
    if period:
        period = int(period)
    if evaluation_periods:
        evaluation_periods = int(evaluation_periods)
    if isinstance(dimensions, string_types):
        dimensions = json.loads(dimensions)
        if not isinstance(dimensions, dict):
            log.error("could not parse dimensions argument: must be json encoding of a dict: '{0}'".format(dimensions))
            return False
    if isinstance(alarm_actions, string_types):
        alarm_actions = alarm_actions.split(",")
    if isinstance(insufficient_data_actions, string_types):
        insufficient_data_actions = insufficient_data_actions.split(",")
    if isinstance(ok_actions, string_types):
        ok_actions = ok_actions.split(",")

    # convert provided action names into ARN's
    if alarm_actions:
        alarm_actions = convert_to_arn(alarm_actions,
                                       region=region,
                                       key=key,
                                       keyid=keyid,
                                       profile=profile)
    if insufficient_data_actions:
        insufficient_data_actions = convert_to_arn(insufficient_data_actions,
                                                   region=region,
                                                   key=key,
                                                   keyid=keyid,
                                                   profile=profile)
    if ok_actions:
        ok_actions = convert_to_arn(ok_actions,
                                    region=region,
                                    key=key,
                                    keyid=keyid,
                                    profile=profile)

    conn = _get_conn(region, key, keyid, profile)
    if not conn:
        return False
    alarm = boto.ec2.cloudwatch.alarm.MetricAlarm(
        connection=connection,
        name=name,
        metric=metric,
        namespace=namespace,
        statistic=statistic,
        comparison=comparison,
        threshold=threshold,
        period=period,
        evaluation_periods=evaluation_periods,
        unit=unit,
        description=description,
        dimensions=dimensions,
        alarm_actions=alarm_actions,
        insufficient_data_actions=insufficient_data_actions,
        ok_actions=ok_actions
    )
    conn.create_alarm(alarm)
    log.info('Created/updated alarm {0}'.format(name))
    return True