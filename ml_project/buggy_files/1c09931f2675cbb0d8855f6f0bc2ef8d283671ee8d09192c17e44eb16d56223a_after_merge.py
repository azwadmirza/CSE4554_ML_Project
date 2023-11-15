def execute(trans, tool, mapping_params, history, rerun_remap_job_id=None, collection_info=None, workflow_invocation_uuid=None, invocation_step=None, max_num_jobs=None, job_callback=None, completed_jobs=None, workflow_resource_parameters=None, validate_outputs=False):
    """
    Execute a tool and return object containing summary (output data, number of
    failures, etc...).
    """
    if max_num_jobs:
        assert invocation_step is not None
    if rerun_remap_job_id:
        assert invocation_step is None

    all_jobs_timer = tool.app.execution_timer_factory.get_timer(
        'internals.galaxy.tools.execute.job_batch', BATCH_EXECUTION_MESSAGE
    )

    if invocation_step is None:
        execution_tracker = ToolExecutionTracker(trans, tool, mapping_params, collection_info, completed_jobs=completed_jobs)
    else:
        execution_tracker = WorkflowStepExecutionTracker(trans, tool, mapping_params, collection_info, invocation_step, completed_jobs=completed_jobs)
    execution_cache = ToolExecutionCache(trans)

    def execute_single_job(execution_slice, completed_job):
        job_timer = tool.app.execution_timer_factory.get_timer(
            'internals.galaxy.tools.execute.job_single', SINGLE_EXECUTION_SUCCESS_MESSAGE
        )
        params = execution_slice.param_combination
        if workflow_invocation_uuid:
            params['__workflow_invocation_uuid__'] = workflow_invocation_uuid
        elif '__workflow_invocation_uuid__' in params:
            # Only workflow invocation code gets to set this, ignore user supplied
            # values or rerun parameters.
            del params['__workflow_invocation_uuid__']
        if workflow_resource_parameters:
            params['__workflow_resource_params__'] = workflow_resource_parameters
        elif '__workflow_resource_params__' in params:
            # Only workflow invocation code gets to set this, ignore user supplied
            # values or rerun parameters.
            del params['__workflow_resource_params__']
        if validate_outputs:
            params['__validate_outputs__'] = True
        job, result = tool.handle_single_execution(trans, rerun_remap_job_id, execution_slice, history, execution_cache, completed_job, collection_info, job_callback=job_callback, flush_job=False)
        if job:
            log.debug(job_timer.to_str(tool_id=tool.id, job_id=job.id))
            execution_tracker.record_success(execution_slice, job, result)
        else:
            execution_tracker.record_error(result)

    tool_action = tool.tool_action
    if hasattr(tool_action, "check_inputs_ready"):
        for params in execution_tracker.param_combinations:
            # This will throw an exception if the tool is not ready.
            tool_action.check_inputs_ready(
                tool,
                trans,
                params,
                history,
                execution_cache=execution_cache,
                collection_info=collection_info,
            )

    execution_tracker.ensure_implicit_collections_populated(history, mapping_params.param_template)
    job_count = len(execution_tracker.param_combinations)

    jobs_executed = 0
    has_remaining_jobs = False
    execution_slice = None

    for i, execution_slice in enumerate(execution_tracker.new_execution_slices()):
        if max_num_jobs and jobs_executed >= max_num_jobs:
            has_remaining_jobs = True
            break
        else:
            execute_single_job(execution_slice, completed_jobs[i])
            history = execution_slice.history or history
            jobs_executed += 1

    if execution_slice:
        # a side effect of adding datasets to a history is a commit within db_next_hid (even with flush=False).
        history.add_pending_datasets()
    else:
        # Make sure collections, implicit jobs etc are flushed even if there are no precreated output datasets
        trans.sa_session.flush()
    tool_id = tool.id
    for job in execution_tracker.successful_jobs:
        # Put the job in the queue if tracking in memory
        tool.app.job_manager.enqueue(job, tool=tool, flush=False)
        trans.log_event("Added job to the job queue, id: %s" % str(job.id), tool_id=tool_id)
    trans.sa_session.flush()

    if has_remaining_jobs:
        raise PartialJobExecution(execution_tracker)
    else:
        execution_tracker.finalize_dataset_collections(trans)

    log.debug(all_jobs_timer.to_str(job_count=job_count, tool_id=tool.id))
    return execution_tracker