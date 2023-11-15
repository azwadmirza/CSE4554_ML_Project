    def _show(self, target, commands, outs, locked):
        import networkx
        from dvc.stage import Stage

        stage = Stage.load(self.repo, target)
        G = self.repo.graph()[0]
        stages = networkx.get_node_attributes(G, "stage")
        node = os.path.relpath(stage.path, self.repo.root_dir)
        nodes = networkx.dfs_postorder_nodes(G, node)

        if locked:
            nodes = [n for n in nodes if stages[n].locked]

        for n in nodes:
            if commands:
                logger.info(stages[n].cmd)
            elif outs:
                for out in stages[n].outs:
                    logger.info(str(out))
            else:
                logger.info(n)