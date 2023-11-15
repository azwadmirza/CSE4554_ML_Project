def acr_task_create(cmd,  # pylint: disable=too-many-locals
                    client,
                    task_name,
                    registry_name,
                    context_path,
                    file=None,
                    cmd_value=None,
                    git_access_token=None,
                    image_names=None,
                    status='Enabled',
                    platform=None,
                    cpu=DEFAULT_CPU,
                    timeout=DEFAULT_TIMEOUT_IN_SEC,
                    values=None,
                    source_trigger_name='defaultSourceTriggerName',
                    commit_trigger_enabled=True,
                    pull_request_trigger_enabled=True,
                    branch='master',
                    no_push=False,
                    no_cache=False,
                    arg=None,
                    secret_arg=None,
                    set_value=None,
                    set_secret=None,
                    base_image_trigger_name='defaultBaseimageTriggerName',
                    base_image_trigger_enabled=True,
                    base_image_trigger_type='Runtime',
                    resource_group_name=None,
                    assign_identity=None,
                    target=None,
                    auth_mode=None):

    registry, resource_group_name = get_registry_by_name(
        cmd.cli_ctx, registry_name, resource_group_name)

    if context_path.lower() == NULL_CONTEXT:
        context_path = None
        commit_trigger_enabled = False
        pull_request_trigger_enabled = False

    if (commit_trigger_enabled or pull_request_trigger_enabled) and not git_access_token:
        raise CLIError("If source control trigger is enabled [--commit-trigger-enabled] or "
                       "[--pull-request-trigger-enabled] --git-access-token must be provided.")

    if cmd_value and file:
        raise CLIError(
            "Task can be created with either "
            "--cmd myCommand -c /dev/null or "
            "-f myFile -c myContext, but not both.")

    step = create_task_step(
        context_path=context_path,
        cmd=cmd,
        file=file,
        image_names=image_names,
        values=values,
        git_access_token=git_access_token,
        set_value=set_value,
        set_secret=set_secret,
        no_push=no_push,
        no_cache=no_cache,
        arg=arg,
        secret_arg=secret_arg,
        target=target,
        cmd_value=cmd_value,
        timeout=timeout)

    SourceControlType, SourceTriggerEvent = cmd.get_models(
        'SourceControlType', 'SourceTriggerEvent')
    source_control_type = SourceControlType.visual_studio_team_service.value
    if context_path is not None and 'GITHUB.COM' in context_path.upper():
        source_control_type = SourceControlType.github.value

    source_triggers = None
    source_trigger_events = []
    if commit_trigger_enabled:
        source_trigger_events.append(SourceTriggerEvent.commit.value)
    if pull_request_trigger_enabled:
        source_trigger_events.append(SourceTriggerEvent.pullrequest.value)
    # if source_trigger_events contains any event types we assume they are enabled
    if source_trigger_events:
        SourceTrigger, SourceProperties, AuthInfo, TriggerStatus = cmd.get_models(
            'SourceTrigger', 'SourceProperties', 'AuthInfo', 'TriggerStatus')
        source_triggers = [
            SourceTrigger(
                source_repository=SourceProperties(
                    source_control_type=source_control_type,
                    repository_url=context_path,
                    branch=branch,
                    source_control_auth_properties=AuthInfo(
                        token=git_access_token,
                        token_type=DEFAULT_TOKEN_TYPE,
                        scope='repo'
                    )
                ),
                source_trigger_events=source_trigger_events,
                status=TriggerStatus.enabled.value,
                name=source_trigger_name
            )
        ]

    base_image_trigger = None
    if base_image_trigger_enabled:
        BaseImageTrigger, TriggerStatus = cmd.get_models(
            'BaseImageTrigger', 'TriggerStatus')
        base_image_trigger = BaseImageTrigger(
            base_image_trigger_type=base_image_trigger_type,
            status=TriggerStatus.enabled.value if base_image_trigger_enabled else TriggerStatus.disabled.value,
            name=base_image_trigger_name
        )

    platform_os, platform_arch, platform_variant = get_validate_platform(cmd, platform)

    Task, PlatformProperties, AgentProperties, TriggerProperties = cmd.get_models(
        'Task', 'PlatformProperties', 'AgentProperties', 'TriggerProperties')

    identity = None
    if assign_identity is not None:
        identity = _build_identities_info(cmd, assign_identity)

    task_create_parameters = Task(
        identity=identity,
        location=registry.location,
        step=step,
        platform=PlatformProperties(
            os=platform_os,
            architecture=platform_arch,
            variant=platform_variant
        ),
        status=status,
        timeout=timeout,
        agent_configuration=AgentProperties(
            cpu=cpu
        ),
        trigger=TriggerProperties(
            source_triggers=source_triggers,
            base_image_trigger=base_image_trigger
        ),
        credentials=get_custom_registry_credentials(
            cmd=cmd,
            auth_mode=auth_mode
        )
    )

    try:
        return client.create(resource_group_name=resource_group_name,
                             registry_name=registry_name,
                             task_name=task_name,
                             task_create_parameters=task_create_parameters)
    except ValidationError as e:
        raise CLIError(e)