    def visualize(
        self, flow_state: "prefect.engine.state.State" = None, filename: str = None
    ) -> object:
        """
        Creates graphviz object for representing the current flow; this graphviz
        object will be rendered inline if called from an IPython notebook, otherwise
        it will be rendered in a new window.  If a `filename` is provided, the object
        will not be rendered and instead saved to the location specified.

        Args:
            - flow_state (State, optional): flow state object used to optionally color the nodes
            - filename (str, optional): a filename specifying a location to save this visualization to; if provided,
                the visualization will not be rendered automatically

        Raises:
            - ImportError: if `graphviz` is not installed
        """

        try:
            import graphviz
        except ImportError:
            msg = (
                "This feature requires graphviz.\n"
                "Try re-installing prefect with `pip install 'prefect[viz]'`"
            )
            raise ImportError(msg)

        def get_color(task: Task, map_index: int = None) -> str:
            assert flow_state
            assert isinstance(flow_state.result, dict)

            if map_index is not None:
                state = flow_state.result[task].map_states[map_index]
            else:
                state = flow_state.result.get(task)
            if state is not None:
                assert state is not None  # mypy assert
                return state.color + "80"
            return "#00000080"

        graph = graphviz.Digraph()

        for t in self.tasks:
            is_mapped = any(edge.mapped for edge in self.edges_to(t))
            shape = "box" if is_mapped else "ellipse"
            name = "{} <map>".format(t.name) if is_mapped else t.name
            if is_mapped and flow_state:
                assert isinstance(flow_state.result, dict)
                for map_index, _ in enumerate(flow_state.result[t].map_states):
                    kwargs = dict(
                        color=get_color(t, map_index=map_index),
                        style="filled",
                        colorscheme="svg",
                    )
                    graph.node(str(id(t)) + str(map_index), name, shape=shape, **kwargs)
            else:
                kwargs = (
                    {}
                    if not flow_state
                    else dict(color=get_color(t), style="filled", colorscheme="svg")
                )
                graph.node(str(id(t)), name, shape=shape, **kwargs)

        for e in self.edges:
            style = "dashed" if e.mapped else None
            if (
                e.mapped
                or any(edge.mapped for edge in self.edges_to(e.downstream_task))
            ) and flow_state:
                assert isinstance(flow_state.result, dict)
                for map_index, _ in enumerate(
                    flow_state.result[e.downstream_task].map_states
                ):
                    upstream_id = str(id(e.upstream_task))
                    if any(edge.mapped for edge in self.edges_to(e.upstream_task)):
                        upstream_id += str(map_index)
                    graph.edge(
                        upstream_id,
                        str(id(e.downstream_task)) + str(map_index),
                        e.key,
                        style=style,
                    )
            else:
                graph.edge(
                    str(id(e.upstream_task)),
                    str(id(e.downstream_task)),
                    e.key,
                    style=style,
                )

        if filename:
            graph.render(filename, view=False)
        else:
            try:
                from IPython import get_ipython

                assert get_ipython().config.get("IPKernelApp") is not None
            except Exception:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.close()
                    try:
                        graph.render(tmp.name, view=True)
                    except graphviz.backend.ExecutableNotFound:
                        msg = "It appears you do not have Graphviz installed, or it is not on your PATH.\n"
                        msg += "Please install Graphviz from http://www.graphviz.org/download/\n"
                        msg += "And note: just installing the `graphviz` python package is not sufficient!"
                        raise graphviz.backend.ExecutableNotFound(msg)
                    finally:
                        os.unlink(tmp.name)

        return graph