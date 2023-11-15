def _reproduce(self, target, **kwargs):
    import networkx as nx
    from dvc.stage import Stage

    stage = Stage.load(self, target)
    G = self.graph()[1]
    stages = nx.get_node_attributes(G, "stage")
    node = relpath(stage.path, self.root_dir)

    return _reproduce_stages(G, stages, node, **kwargs)