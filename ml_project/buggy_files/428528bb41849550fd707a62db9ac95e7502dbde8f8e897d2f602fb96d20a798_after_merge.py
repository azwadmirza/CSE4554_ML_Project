def get_location_completion_list(cmd, prefix, namespace,**kwargs):  # pylint: disable=unused-argument
    result = get_subscription_locations(cmd.cli_ctx)
    return [l.name for l in result]