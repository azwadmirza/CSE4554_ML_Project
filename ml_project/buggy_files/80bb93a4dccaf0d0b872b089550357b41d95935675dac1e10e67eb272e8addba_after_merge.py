    def collect(self, target, with_deps=False, recursive=False):
        import networkx as nx
        from dvc.stage import Stage

        if not target or (recursive and os.path.isdir(target)):
            return self.active_stages(target)

        stage = Stage.load(self, target)
        if not with_deps:
            return [stage]

        node = relpath(stage.path, self.root_dir)
        G = self._get_pipeline(node)

        ret = []
        for n in nx.dfs_postorder_nodes(G, node):
            ret.append(G.node[n]["stage"])

        return ret