def _reproduce(
    self,
    target,
    single_item=False,
    force=False,
    dry=False,
    interactive=False,
    ignore_build_cache=False,
    no_commit=False,
    downstream=False,
):
    import networkx as nx
    from dvc.stage import Stage

    stage = Stage.load(self, target)
    G = self.graph()[1]
    stages = nx.get_node_attributes(G, "stage")
    node = os.path.relpath(stage.path, self.root_dir)

    if single_item:
        ret = _reproduce_stage(
            stages, node, force, dry, interactive, no_commit
        )
    else:
        ret = _reproduce_stages(
            G,
            stages,
            node,
            force,
            dry,
            interactive,
            ignore_build_cache,
            no_commit,
            downstream,
        )

    return ret