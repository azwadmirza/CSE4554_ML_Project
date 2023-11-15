def minimize_and_clip(optimizer, objective, var_list, clip_val=10.0):
    """Minimized `objective` using `optimizer` w.r.t. variables in
    `var_list` while ensure the norm of the gradients for each
    variable is clipped to `clip_val`
    """
    # Accidentally passing values < 0.0 will break all gradients.
    assert clip_val > 0.0, clip_val

    if tf.executing_eagerly():
        tape = optimizer.tape
        grads_and_vars = list(
            zip(list(tape.gradient(objective, var_list)), var_list))
    else:
        grads_and_vars = optimizer.compute_gradients(
            objective, var_list=var_list)

    for i, (grad, var) in enumerate(grads_and_vars):
        if grad is not None:
            grads_and_vars[i] = (tf.clip_by_norm(grad, clip_val), var)
    return grads_and_vars