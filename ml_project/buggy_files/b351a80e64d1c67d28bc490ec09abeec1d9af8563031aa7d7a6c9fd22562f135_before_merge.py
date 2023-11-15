def job_to_cwl(job, dag, outputs, inputs):
    """Convert a job with its dependencies to a CWL workflow step.
    """

    if job.dynamic_output:
        raise WorkflowError("Dynamic output is not supported by CWL conversion.")
    for f in job.output:
        if os.path.isabs(f):
            raise WorkflowError(
                "All output files have to be relative to the " "working directory."
            )

    get_output_id = lambda job, i: "#main/job-{}/{}".format(job.jobid, i)

    dep_ids = {
        o: get_output_id(dep, i)
        for dep, files in dag.dependencies[job].items()
        for i, o in enumerate(dep.output)
        if o in files
    }
    files = [f for f in job.input if f not in dep_ids]
    if job.conda_env_file:
        files.add(os.path.relpath(job.conda_env_file))

    out = [get_output_id(job, i) for i, _ in enumerate(job.output)]

    def workdir_entry(i, f):
        location = "??inputs.input_files[{}].location??".format(i)
        if f.is_directory:
            entry = {
                "class": "Directory",
                "basename": os.path.basename(f),
                "location": location,
            }
        else:
            entry = {
                "class": "File",
                "basename": os.path.basename(f),
                "location": location,
            }
        return "$({})".format(
            json.dumps(outer_entry(f, entry)).replace('"??', "").replace('??"', "")
        ).replace('"', "'")

    def outer_entry(f, entry):
        parent = os.path.dirname(f)
        if parent:
            return outer_entry(
                parent,
                {
                    "class": "Directory",
                    "basename": os.path.basename(parent),
                    "listing": [entry],
                },
            )
        else:
            return entry

    if job in dag.targetjobs:
        # TODO this maps output files into the cwd after the workflow is complete.
        # We need to find a way to define subdirectories though. Otherwise,
        # there can be name clashes, and it will also become very crowded.
        outputs.append(
            {
                "type": {"type": "array", "items": "File"},
                "outputSource": "#main/job-{}/output_files".format(job.jobid),
                "id": "#main/output/job-{}".format(job.jobid),
            }
        )

    cwl = {
        "run": "#snakemake-job",
        "requirements": {
            "InitialWorkDirRequirement": {
                "listing": [
                    {"writable": True, "entry": workdir_entry(i, f)}
                    for i, f in enumerate(
                        chain(
                            files,
                            (f for dep in dag.dependencies[job] for f in dep.output),
                        )
                    )
                ]
            }
        },
        "in": {
            "cores": {"default": job.threads},
            "target_files": {"default": job.output.plainstrings()},
            "rules": {"default": [job.rule.name]},
        },
        "out": ["output_files"],
        "id": "#main/job-{}".format(job.jobid),
    }
    if files:
        inputs.append(
            {
                "type": {"type": "array", "items": "File"},
                "default": [{"class": "File", "location": f} for f in files],
                "id": "#main/input/job-{}".format(job.jobid),
            }
        )

    input_files = []
    if files:
        input_files.append("#main/input/job-{}".format(job.jobid))
    input_files.extend(
        "#main/job-{}/output_files".format(dep.jobid) for dep in dag.dependencies[job]
    )

    cwl["in"]["input_files"] = {"source": input_files, "linkMerge": "merge_flattened"}

    return cwl