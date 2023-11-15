def reproduce(
    self: "Repo",
    targets=None,
    recursive=False,
    pipeline=False,
    all_pipelines=False,
    **kwargs,
):
    glob = kwargs.pop("glob", False)
    accept_group = not glob

    if isinstance(targets, str):
        targets = [targets]

    if not all_pipelines and targets is None:
        from dvc.dvcfile import PIPELINE_FILE

        targets = [PIPELINE_FILE]

    interactive = kwargs.get("interactive", False)
    if not interactive:
        kwargs["interactive"] = self.config["core"].get("interactive", False)

    active_graph = _get_active_graph(self.graph)
    active_pipelines = get_pipelines(active_graph)

    stages = set()
    if pipeline or all_pipelines:
        if all_pipelines:
            pipelines = active_pipelines
        else:
            pipelines = []
            for target in targets:
                stage = self.stage.get_target(target)
                pipelines.append(get_pipeline(active_pipelines, stage))

        for pipeline in pipelines:
            for stage in pipeline:
                if pipeline.in_degree(stage) == 0:
                    stages.add(stage)
    else:
        for target in targets:
            stages.update(
                self.stage.collect(
                    target,
                    recursive=recursive,
                    graph=active_graph,
                    accept_group=accept_group,
                    glob=glob,
                )
            )

    return _reproduce_stages(active_graph, list(stages), **kwargs)