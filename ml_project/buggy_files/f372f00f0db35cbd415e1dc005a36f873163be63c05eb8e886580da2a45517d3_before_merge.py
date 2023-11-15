def _get_cloudwatch_logs_url(context, start_time):
    # type: (Any, datetime) -> str
    """
    Generates a CloudWatchLogs console URL based on the context object

    Arguments:
        context {Any} -- context from lambda handler

    Returns:
        str -- AWS Console URL to logs.
    """
    formatstring = "%Y-%m-%dT%H:%M:%SZ"

    url = (
        "https://console.aws.amazon.com/cloudwatch/home?region={region}"
        "#logEventViewer:group={log_group};stream={log_stream}"
        ";start={start_time};end={end_time}"
    ).format(
        region=environ.get("AWS_REGION"),
        log_group=context.log_group_name,
        log_stream=context.log_stream_name,
        start_time=(start_time - timedelta(seconds=1)).strftime(formatstring),
        end_time=(datetime.utcnow() + timedelta(seconds=2)).strftime(formatstring),
    )

    return url