def minimize_and_clip(optimizer, objective, var_list, clip_val=10.0):
    """Minimized `objective` using `optimizer` w.r.t. variables in
    `var_list` while ensure the norm of the gradients for each
    variable is clipped to `clip_val`
    """
    # Accidentally passing values < 0.0 will break all gradients.
    assert clip_val is None or clip_val > 0.0, clip_val

    if tf.executing_eagerly():
        tape = optimizer.tape
        grads_and_vars = list(
            zip(list(tape.gradient(objective, var_list)), var_list))
    else:
        grads_and_vars = optimizer.compute_gradients(
            objective, var_list=var_list)

    return [(tf.clip_by_norm(g, clip_val) if clip_val is not None else g, v)
            for (g, v) in grads_and_vars if g is not None]