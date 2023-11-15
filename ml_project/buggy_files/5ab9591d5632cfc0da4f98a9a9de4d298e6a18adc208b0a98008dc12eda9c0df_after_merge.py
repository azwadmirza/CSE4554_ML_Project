def _taskshandlers_children(basedir, k, v, parent_type: FileType) -> List:
    results = []
    if v is None:
        raise MatchError(
            message="A malformed block was encountered while loading a block.",
            rule=RuntimeErrorRule)
    for th in v:

        # ignore empty tasks, `-`
        if not th:
            continue

        with contextlib.suppress(LookupError):
            children = _get_task_handler_children_for_tasks_or_playbooks(
                th, basedir, k, parent_type,
            )
            results.append(children)
            continue

        if 'include_role' in th or 'import_role' in th:  # lgtm [py/unreachable-statement]
            th = normalize_task_v2(th)
            _validate_task_handler_action_for_role(th['action'])
            results.extend(_roles_children(basedir, k, [th['action'].get("name")],
                                           parent_type,
                                           main=th['action'].get('tasks_from', 'main')))
            continue

        if 'block' not in th:
            continue

        results.extend(_taskshandlers_children(basedir, k, th['block'], parent_type))
        if 'rescue' in th:
            results.extend(_taskshandlers_children(basedir, k, th['rescue'], parent_type))
        if 'always' in th:
            results.extend(_taskshandlers_children(basedir, k, th['always'], parent_type))

    return results