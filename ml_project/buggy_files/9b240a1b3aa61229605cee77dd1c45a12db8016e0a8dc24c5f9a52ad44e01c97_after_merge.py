def _update_start_vals(a, b, model):
    """Update a with b, without overwriting existing keys. Values specified for
    transformed variables on the original scale are also transformed and inserted.
    """
    if model is not None:
        for free_RV in model.free_RVs:
            tname = free_RV.name
            for name in a:
                if is_transformed_name(tname) and get_untransformed_name(tname) == name:
                    transform_func = [d.transformation for d in model.deterministics if d.name == name]
                    if transform_func:
                        b[tname] = transform_func[0].forward_val(a[name], point=b).eval()

    a.update({k: v for k, v in b.items() if k not in a})