def reset(module, conn, name, values):
    """ Reset ElastiCache parameter group if the current information is different from the new information. """
    # used to compare with the reset parameters' dict to see if there have been changes
    old_parameters_dict = make_current_modifiable_param_dict(module, conn, name)

    format_parameters = []

    # determine whether to reset all or specific parameters
    if values:
        all_parameters = False
        format_parameters = []
        for key in values:
            value = to_text(values[key])
            format_parameters.append({'ParameterName': key, 'ParameterValue': value})
    else:
        all_parameters = True

    try:
        response = conn.reset_cache_parameter_group(CacheParameterGroupName=name, ParameterNameValues=format_parameters, ResetAllParameters=all_parameters)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Unable to reset cache parameter group.", exception=traceback.format_exc(), **camel_dict_to_snake_dict(e.response))

    # determine changed
    new_parameters_dict = make_current_modifiable_param_dict(module, conn, name)
    changed = check_changed_parameter_values(values, old_parameters_dict, new_parameters_dict)

    return response, changed