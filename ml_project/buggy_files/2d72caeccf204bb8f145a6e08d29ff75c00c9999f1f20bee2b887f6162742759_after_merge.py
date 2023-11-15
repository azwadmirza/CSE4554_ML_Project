def _container_generic_transform(arg, context, klass, iterables, build_elts):
    if isinstance(arg, klass):
        return arg
    elif isinstance(arg, iterables):
        if all(isinstance(elt, nodes.Const) for elt in arg.elts):
            elts = [elt.value for elt in arg.elts]
        else:
            # TODO: Does not handle deduplication for sets.
            elts = []
            for element in arg.elts:
                if not element:
                    continue
                inferred = helpers.safe_infer(element, context=context)
                if inferred:
                    evaluated_object = nodes.EvaluatedObject(
                        original=element, value=inferred
                    )
                    elts.append(evaluated_object)
    elif isinstance(arg, nodes.Dict):
        # Dicts need to have consts as strings already.
        if not all(isinstance(elt[0], nodes.Const) for elt in arg.items):
            raise UseInferenceDefault()
        elts = [item[0].value for item in arg.items]
    elif isinstance(arg, nodes.Const) and isinstance(
        arg.value, (six.string_types, six.binary_type)
    ):
        elts = arg.value
    else:
        return
    return klass.from_elements(elts=build_elts(elts))