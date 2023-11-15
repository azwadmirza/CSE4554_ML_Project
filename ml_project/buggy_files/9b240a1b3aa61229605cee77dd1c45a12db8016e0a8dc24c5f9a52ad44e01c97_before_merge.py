def _update_start_vals(a, b, model):
    """Update a with b, without overwriting existing keys. Values specified for
    transformed variables on the original scale are also transformed and inserted.
    """
    for name in a:
        for tname in b:
            if is_transformed_name(tname) and get_untransformed_name(tname) == name:
                transform_func = [d.transformation for d in model.deterministics if d.name == name]
                if transform_func:
                    b[tname] = transform_func[0].forward(a[name]).eval()

    a.update({k: v for k, v in b.items() if k not in a})