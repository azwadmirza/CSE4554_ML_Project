def main():
    parser = argparse.ArgumentParser(description="Spawn tasks for bugbug data pipeline")
    parser.add_argument("data_pipeline_json")

    args = parser.parse_args()
    decision_task_id = os.environ.get("TASK_ID")
    options = get_taskcluster_options()
    add_self = False
    if decision_task_id:
        add_self = True
        task_group_id = decision_task_id
    else:
        task_group_id = taskcluster.utils.slugId()
    keys = {"taskGroupId": task_group_id}

    id_mapping = {}

    # First pass, do the template rendering and dependencies resolution
    tasks = []

    with open(args.data_pipeline_json) as pipeline_file:
        raw_tasks = yaml.safe_load(pipeline_file.read())

    version = os.getenv("TAG", "latest")
    context = {"version": version}
    rendered = jsone.render(raw_tasks, context)

    for task in rendered["tasks"]:
        # We need to generate new unique task ids for taskcluster to be happy
        # but need to identify dependencies across tasks. So we create a
        # mapping between an internal ID and the generate ID

        task_id = taskcluster.utils.slugId()
        task_internal_id = task["ID"]

        if task_internal_id in id_mapping:
            raise ValueError(f"Conflicting IDs {task_internal_id}")

        # Store each task ID in the id_mapping dictionary before processing dependencies.
        # This way, tasks can be defined in any order.
        id_mapping[task_internal_id] = task_id

    for task in rendered["tasks"]:
        task_internal_id = task.pop("ID")
        task_id = id_mapping[task_internal_id]

        for key, value in keys.items():
            task[key] = value

        task_payload = task["payload"]

        if "env" in task_payload and task_payload["env"]:
            task_payload["env"]["TAG"] = version
        else:
            task_payload["env"] = {
                "TAG": version,
            }

        # Process the dependencies
        new_dependencies = []
        for dependency in task.get("dependencies", []):
            new_dependencies.append(id_mapping[dependency])

        if add_self:
            new_dependencies.append(decision_task_id)

        task["dependencies"] = new_dependencies

        tasks.append((task_id, task))

    # Now sends them
    queue = taskcluster.Queue(options)
    try:
        for task_id, task_payload in tasks:
            queue.createTask(task_id, task_payload)

        print(f"https://community-tc.services.mozilla.com/tasks/groups/{task_group_id}")
    except taskcluster.exceptions.TaskclusterAuthFailure as e:
        print(f"TaskclusterAuthFailure: {e.body}", file=sys.stderr)
        raise