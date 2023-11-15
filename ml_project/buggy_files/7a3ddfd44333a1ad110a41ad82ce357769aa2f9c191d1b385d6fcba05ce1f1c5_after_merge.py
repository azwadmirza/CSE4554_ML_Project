    def graph(self, stages=None, from_directory=None):
        """Generate a graph by using the given stages on the given directory

        The nodes of the graph are the stage's path relative to the root.

        Edges are created when the output of one stage is used as a
        dependency in other stage.

        The direction of the edges goes from the stage to its dependency:

        For example, running the following:

            $ dvc run -o A "echo A > A"
            $ dvc run -d A -o B "echo B > B"
            $ dvc run -d B -o C "echo C > C"

        Will create the following graph:

               ancestors <--
                           |
                C.dvc -> B.dvc -> A.dvc
                |          |
                |          --> descendants
                |
                ------- pipeline ------>
                           |
                           v
              (weakly connected components)

        Args:
            stages (list): used to build a graph, if None given, use the ones
                on the `from_directory`.

            from_directory (str): directory where to look at for stages, if
                None is given, use the current working directory

        Raises:
            OutputDuplicationError: two outputs with the same path
            StagePathAsOutputError: stage inside an output directory
            OverlappingOutputPathsError: output inside output directory
            CyclicGraphError: resulting graph has cycles
        """
        import networkx as nx
        from dvc.exceptions import (
            OutputDuplicationError,
            StagePathAsOutputError,
            OverlappingOutputPathsError,
        )

        G = nx.DiGraph()
        G_active = nx.DiGraph()
        stages = stages or self.stages(from_directory, check_dag=False)
        stages = [stage for stage in stages if stage]
        outs = []

        for stage in stages:
            for out in stage.outs:
                existing = []
                for o in outs:
                    if o.path_info == out.path_info:
                        existing.append(o.stage)

                    in_o_dir = out.path_info.isin(o.path_info)
                    in_out_dir = o.path_info.isin(out.path_info)
                    if in_o_dir or in_out_dir:
                        raise OverlappingOutputPathsError(o, out)

                if existing:
                    stages = [stage.relpath, existing[0].relpath]
                    raise OutputDuplicationError(str(out), stages)

                outs.append(out)

        for stage in stages:
            stage_path_info = PathInfo(stage.path)
            for out in outs:
                if stage_path_info.isin(out.path_info):
                    raise StagePathAsOutputError(stage.wdir, stage.relpath)

        for stage in stages:
            node = relpath(stage.path, self.root_dir)

            G.add_node(node, stage=stage)
            G_active.add_node(node, stage=stage)

            for dep in stage.deps:
                for out in outs:
                    if (
                        out.path_info != dep.path_info
                        and not dep.path_info.isin(out.path_info)
                        and not out.path_info.isin(dep.path_info)
                    ):
                        continue

                    dep_stage = out.stage
                    dep_node = relpath(dep_stage.path, self.root_dir)
                    G.add_node(dep_node, stage=dep_stage)
                    G.add_edge(node, dep_node)
                    if not stage.locked:
                        G_active.add_node(dep_node, stage=dep_stage)
                        G_active.add_edge(node, dep_node)

        self._check_cyclic_graph(G)

        return G, G_active