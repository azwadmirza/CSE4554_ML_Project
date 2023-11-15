    def render_dot(self, filename_prefix="numba_ir"):
        """Render the CFG of the IR with GraphViz DOT via the
        ``graphviz`` python binding.

        Returns
        -------
        g : graphviz.Digraph
            Use `g.view()` to open the graph in the default PDF application.
        """

        try:
            import graphviz as gv
        except ImportError:
            raise ImportError(
                "The feature requires `graphviz` but it is not available. "
                "Please install with `pip install graphviz`"
            )
        g = gv.Digraph(
            filename="{}{}.dot".format(
                filename_prefix,
                self.func_id.unique_name,
            )
        )
        # Populate the nodes
        for k, blk in self.blocks.items():
            with StringIO() as sb:
                blk.dump(sb)
                label = sb.getvalue()
            label = ''.join(
                ['  {}\l'.format(x) for x in label.splitlines()],
            )
            label = "block {}\l".format(k) + label
            g.node(str(k), label=label, shape='rect')
        # Populate the edges
        for src, blk in self.blocks.items():
            for dst in blk.terminator.get_targets():
                g.edge(str(src), str(dst))
        return g