def get_resource_group_completion_list(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
    result = get_resource_groups(cmd.cli_ctx)
    return [l.name for l in result]