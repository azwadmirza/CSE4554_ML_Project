def extract_steps(trans, history=None, job_ids=None, dataset_ids=None, dataset_collection_ids=None, dataset_names=None, dataset_collection_names=None):
    # Ensure job_ids and dataset_ids are lists (possibly empty)
    if job_ids is None:
        job_ids = []
    elif type(job_ids) is not list:
        job_ids = [job_ids]
    if dataset_ids is None:
        dataset_ids = []
    elif type(dataset_ids) is not list:
        dataset_ids = [dataset_ids]
    if dataset_collection_ids is None:
        dataset_collection_ids = []
    elif type(dataset_collection_ids) is not list:
        dataset_collection_ids = [dataset_collection_ids]
    # Convert both sets of ids to integers
    job_ids = [int(_) for _ in job_ids]
    dataset_ids = [int(_) for _ in dataset_ids]
    dataset_collection_ids = [int(_) for _ in dataset_collection_ids]
    # Find each job, for security we (implicitly) check that they are
    # associated with a job in the current history.
    summary = WorkflowSummary(trans, history)
    jobs = summary.jobs
    steps = []
    hid_to_output_pair = {}
    # Input dataset steps
    for i, hid in enumerate(dataset_ids):
        step = model.WorkflowStep()
        step.type = 'data_input'
        if dataset_names:
            name = dataset_names[i]
        else:
            name = "Input Dataset"
        step.tool_inputs = dict(name=name)
        hid_to_output_pair[hid] = (step, 'output')
        steps.append(step)
    for i, hid in enumerate(dataset_collection_ids):
        step = model.WorkflowStep()
        step.type = 'data_collection_input'
        if hid not in summary.collection_types:
            raise exceptions.RequestParameterInvalidException("hid %s does not appear to be a collection" % hid)
        collection_type = summary.collection_types[hid]
        if dataset_collection_names:
            name = dataset_collection_names[i]
        else:
            name = "Input Dataset Collection"
        step.tool_inputs = dict(name=name, collection_type=collection_type)
        hid_to_output_pair[hid] = (step, 'output')
        steps.append(step)
    # Tool steps
    for job_id in job_ids:
        if job_id not in summary.job_id2representative_job:
            log.warning("job_id %s not found in job_id2representative_job %s" % (job_id, summary.job_id2representative_job))
            raise AssertionError("Attempt to create workflow with job not connected to current history")
        job = summary.job_id2representative_job[job_id]
        tool_inputs, associations = step_inputs(trans, job)
        step = model.WorkflowStep()
        step.type = 'tool'
        step.tool_id = job.tool_id
        step.tool_version = job.tool_version
        step.tool_inputs = tool_inputs
        # NOTE: We shouldn't need to do two passes here since only
        #       an earlier job can be used as an input to a later
        #       job.
        for other_hid, input_name in associations:
            if job in summary.implicit_map_jobs:
                an_implicit_output_collection = jobs[job][0][1]
                input_collection = an_implicit_output_collection.find_implicit_input_collection(input_name)
                if input_collection:
                    other_hid = input_collection.hid
                else:
                    log.info("Cannot find implicit input collection for %s" % input_name)
            if other_hid in hid_to_output_pair:
                step_input = step.get_or_add_input(input_name)
                other_step, other_name = hid_to_output_pair[other_hid]
                conn = model.WorkflowStepConnection()
                conn.input_step_input = step_input
                # Should always be connected to an earlier step
                conn.output_step = other_step
                conn.output_name = other_name
        steps.append(step)
        # Store created dataset hids
        for assoc in (job.output_datasets + job.output_dataset_collection_instances):
            assoc_name = assoc.name
            if ToolOutputCollectionPart.is_named_collection_part_name(assoc_name):
                continue
            if job in summary.implicit_map_jobs:
                hid = None
                for implicit_pair in jobs[job]:
                    query_assoc_name, dataset_collection = implicit_pair
                    if query_assoc_name == assoc_name or assoc_name.startswith("__new_primary_file_%s|" % query_assoc_name):
                        hid = dataset_collection.hid
                if hid is None:
                    template = "Failed to find matching implicit job - job id is %s, implicit pairs are %s, assoc_name is %s."
                    message = template % (job.id, jobs[job], assoc_name)
                    log.warning(message)
                    raise Exception("Failed to extract job.")
            else:
                if hasattr(assoc, "dataset"):
                    hid = assoc.dataset.hid
                else:
                    hid = assoc.dataset_collection_instance.hid
            hid_to_output_pair[hid] = (step, assoc.name)
    return steps