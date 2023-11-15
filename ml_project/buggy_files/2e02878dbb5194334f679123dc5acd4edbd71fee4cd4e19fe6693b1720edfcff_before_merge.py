def reproduce(
    self,
    target=None,
    single_item=False,
    force=False,
    dry=False,
    interactive=False,
    pipeline=False,
    all_pipelines=False,
    ignore_build_cache=False,
    no_commit=False,
    downstream=False,
    recursive=False,
):
    import networkx as nx
    from dvc.stage import Stage

    if not target and not all_pipelines:
        raise ValueError()

    if not interactive:
        config = self.config
        core = config.config[config.SECTION_CORE]
        interactive = core.get(config.SECTION_CORE_INTERACTIVE, False)

    targets = []
    if recursive and os.path.isdir(target):
        G = self.graph(from_directory=target)[1]
        dir_targets = [
            os.path.join(self.root_dir, n) for n in nx.dfs_postorder_nodes(G)
        ]
        targets.extend(dir_targets)
    elif pipeline or all_pipelines:
        if pipeline:
            stage = Stage.load(self, target)
            node = os.path.relpath(stage.path, self.root_dir)
            pipelines = [self._get_pipeline(node)]
        else:
            pipelines = self.pipelines()

        for G in pipelines:
            for node in G.nodes():
                if G.in_degree(node) == 0:
                    targets.append(os.path.join(self.root_dir, node))
    else:
        targets.append(target)

    ret = []
    with self.state:
        for target in targets:
            stages = _reproduce(
                self,
                target,
                single_item=single_item,
                force=force,
                dry=dry,
                interactive=interactive,
                ignore_build_cache=ignore_build_cache,
                no_commit=no_commit,
                downstream=downstream,
            )
            ret.extend(stages)

    return ret