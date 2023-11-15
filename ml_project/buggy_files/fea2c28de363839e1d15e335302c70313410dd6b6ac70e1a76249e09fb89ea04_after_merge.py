    def py__annotations__(self):
        obj = node_classes.Dict(parent=self._instance)

        if not self._instance.returns:
            returns = None
        else:
            returns = self._instance.returns

        args = self._instance.args
        pair_annotations = itertools.chain(
            six.moves.zip(args.args or [], args.annotations),
            six.moves.zip(args.kwonlyargs , args.kwonlyargs_annotations)
        )

        annotations = {
            arg.name: annotation
            for (arg, annotation) in pair_annotations
            if annotation
        }
        if args.varargannotation:
            annotations[args.vararg] = args.varargannotation
        if args.kwargannotation:
            annotations[args.kwarg] = args.kwargannotation
        if returns:
            annotations['return'] = returns

        items = [(node_classes.Const(key, parent=obj), value)
                 for (key, value) in annotations.items()]

        obj.postinit(items)
        return obj