def get_location_completion_list(cli_ctx, prefix, **kwargs):  # pylint: disable=unused-argument
    result = get_subscription_locations(cli_ctx)
    return [l.name for l in result]