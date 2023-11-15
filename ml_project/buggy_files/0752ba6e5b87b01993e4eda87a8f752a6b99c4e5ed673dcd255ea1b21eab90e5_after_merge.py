    def __build_graph(self, target, commands, outs):
        import networkx
        from dvc.stage import Stage

        stage = Stage.load(self.repo, target)
        node = relpath(stage.path, self.repo.root_dir)

        pipelines = list(
            filter(lambda g: node in g.nodes(), self.repo.pipelines())
        )

        assert len(pipelines) == 1
        G = pipelines[0]
        stages = networkx.get_node_attributes(G, "stage")

        nodes = []
        for n in G.nodes():
            stage = stages[n]
            if commands:
                if stage.cmd is None:
                    continue
                nodes.append(stage.cmd)
            elif outs:
                for out in stage.outs:
                    nodes.append(str(out))
            else:
                nodes.append(stage.relpath)

        edges = []
        for e in G.edges():
            from_stage = stages[e[0]]
            to_stage = stages[e[1]]
            if commands:
                if to_stage.cmd is None:
                    continue
                edges.append((from_stage.cmd, to_stage.cmd))
            elif outs:
                for from_out in from_stage.outs:
                    for to_out in to_stage.outs:
                        edges.append((str(from_out), str(to_out)))
            else:
                edges.append((from_stage.relpath, to_stage.relpath))

        return nodes, edges, networkx.is_tree(G)