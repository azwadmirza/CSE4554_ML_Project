    def __init__(
        self,
        nodes: Iterable[Union[Node, "Pipeline"]],
        *,
        name: str = None,
        tags: Union[str, Iterable[str]] = None
    ):  # pylint: disable=missing-type-doc
        """Initialise ``Pipeline`` with a list of ``Node`` instances.

        Args:
            nodes: The list of nodes the ``Pipeline`` will be made of. If you
                provide pipelines among the list of nodes, those pipelines will
                be expanded and all their nodes will become part of this
                new pipeline.
            name: (DEPRECATED, use `tags` method instead) The name of the pipeline.
                If specified, this name will be used to tag all of the nodes
                in the pipeline.
            tags: Optional set of tags to be applied to all the pipeline nodes.

        Raises:
            ValueError:
                When an empty list of nodes is provided, or when not all
                nodes have unique names.
            CircularDependencyError:
                When visiting all the nodes is not
                possible due to the existence of a circular dependency.
            OutputNotUniqueError:
                When multiple ``Node`` instances produce the same output.
        Example:
        ::

            >>> from kedro.pipeline import Pipeline
            >>> from kedro.pipeline import node
            >>>
            >>> # In the following scenario first_ds and second_ds
            >>> # are data sets provided by io. Pipeline will pass these
            >>> # data sets to first_node function and provides the result
            >>> # to the second_node as input.
            >>>
            >>> def first_node(first_ds, second_ds):
            >>>     return dict(third_ds=first_ds+second_ds)
            >>>
            >>> def second_node(third_ds):
            >>>     return third_ds
            >>>
            >>> pipeline = Pipeline([
            >>>     node(first_node, ['first_ds', 'second_ds'], ['third_ds']),
            >>>     node(second_node, dict(third_ds='third_ds'), 'fourth_ds')])
            >>>
            >>> pipeline.describe()
            >>>

        """
        _validate_no_node_list(nodes)
        nodes = list(
            chain.from_iterable(
                [[n] if isinstance(n, Node) else n.nodes for n in nodes]
            )
        )
        _validate_duplicate_nodes(nodes)
        _validate_transcoded_inputs_outputs(nodes)
        _tags = set(_to_list(tags))

        if name:
            warnings.warn(
                "`name` parameter is deprecated for the `Pipeline`"
                " constructor, use `Pipeline.tag` method instead",
                DeprecationWarning,
            )
            _tags.add(name)

        nodes = [n.tag(_tags) for n in nodes]

        self._name = name
        self._nodes_by_name = {node.name: node for node in nodes}
        _validate_unique_outputs(nodes)

        # input -> nodes with input
        self._nodes_by_input = defaultdict(set)  # type: Dict[str, Set[Node]]
        for node in nodes:
            for input_ in node.inputs:
                self._nodes_by_input[_get_transcode_compatible_name(input_)].add(node)

        # output -> node with output
        self._nodes_by_output = {}  # type: Dict[str, Node]
        for node in nodes:
            for output in node.outputs:
                self._nodes_by_output[_get_transcode_compatible_name(output)] = node

        self._nodes = nodes
        self._topo_sorted_nodes = _topologically_sorted(self.node_dependencies)