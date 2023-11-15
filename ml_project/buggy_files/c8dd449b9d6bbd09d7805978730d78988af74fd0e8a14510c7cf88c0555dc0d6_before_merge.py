def _reproduce(self, target, single_item=False, **kwargs):
    import networkx as nx
    from dvc.stage import Stage

    stage = Stage.load(self, target)
    G = self.graph()[1]
    stages = nx.get_node_attributes(G, "stage")
    node = relpath(stage.path, self.root_dir)

    if single_item:
        ret = _reproduce_stage(stages, node, **kwargs)
    else:
        ret = _reproduce_stages(G, stages, node, **kwargs)

    return ret