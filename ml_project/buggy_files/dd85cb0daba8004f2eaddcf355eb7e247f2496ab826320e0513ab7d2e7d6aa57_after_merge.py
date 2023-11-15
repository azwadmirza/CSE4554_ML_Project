def _evaluate_composite_solid_config(context):
    '''Evaluates config for a composite solid and returns CompositeSolidEvaluationResult
    '''
    # Support config mapping override functions
    if not is_solid_container_config(context.config_type):
        return EvaluateValueResult.empty()

    handle = context.config_type.handle

    # If we've already seen this handle, skip -- we've already run the block of code below
    if not handle or handle in context.seen_handles:
        return EvaluateValueResult.empty()

    solid_def = context.pipeline.get_solid(context.config_type.handle).definition
    solid_def_name = context.pipeline.get_solid(handle).definition.name

    has_mapping = isinstance(solid_def, CompositeSolidDefinition) and solid_def.has_config_mapping

    # If there's no config mapping function provided for this composite solid, bail
    if not has_mapping:
        return EvaluateValueResult.empty()

    # We first validate the provided environment config as normal against the composite solid config
    # schema. This will perform a full traversal rooted at the SolidContainerConfigDict and thread
    # errors up to the root
    config_context = context.new_context_with_handle(handle)
    evaluate_value_result = _evaluate_config(config_context)
    if not evaluate_value_result.success:
        return evaluate_value_result

    try:
        mapped_config_value = solid_def.config_mapping.config_fn(
            ConfigMappingContext(run_config=context.run_config),
            # ensure we don't mutate the source environment dict
            frozendict(evaluate_value_result.value.get('config')),
        )
    except Exception:  # pylint: disable=W0703
        return EvaluateValueResult.for_error(
            create_bad_user_config_fn_error(
                context,
                solid_def.config_mapping.config_fn.__name__,
                str(handle),
                solid_def_name,
                traceback.format_exc(),
            )
        )

    if not mapped_config_value:
        return EvaluateValueResult.empty()

    # Perform basic validation on the mapped config value; remaining validation will happen via the
    # evaluate_config call below
    if not isinstance(mapped_config_value, dict):
        return EvaluateValueResult.for_error(
            create_bad_mapping_error(
                context,
                solid_def.config_mapping.config_fn.__name__,
                solid_def_name,
                str(handle),
                mapped_config_value,
            )
        )

    if 'solids' in context.config_value:
        return EvaluateValueResult.for_error(
            create_bad_mapping_solids_key_error(context, solid_def_name, str(handle))
        )

    # We've validated the composite solid config; now validate the mapping fn overrides against the
    # config schema subtree for child solids
    evaluate_value_result = _evaluate_config(
        context.for_mapped_composite_config(handle, mapped_config_value)
    )

    if evaluate_value_result.errors:
        prefix = (
            'Config override mapping function defined by solid {handle_name} from '
            'definition {solid_def_name} {path_msg} caused error: '.format(
                path_msg=get_friendly_path_msg(context.stack),
                handle_name=str(handle),
                solid_def_name=solid_def_name,
            )
        )
        errors = [e._replace(message=prefix + e.message) for e in evaluate_value_result.errors]
        return EvaluateValueResult.for_errors(errors)

    return EvaluateValueResult.for_value(
        dict_merge(context.config_value, {'solids': evaluate_value_result.value})
    )