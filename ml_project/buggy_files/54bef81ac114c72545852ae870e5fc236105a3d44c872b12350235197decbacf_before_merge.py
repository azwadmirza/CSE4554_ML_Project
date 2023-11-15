def get_resource_group_completion_list(cli_ctx, prefix, **kwargs):  # pylint: disable=unused-argument
    result = get_resource_groups(cli_ctx)
    return [l.name for l in result]