def clip_gradients(policy: Policy, optimizer: "tf.keras.optimizers.Optimizer",
                   loss: TensorType) -> ModelGradients:
    if policy.config["grad_clip"] is not None:
        grads_and_vars = minimize_and_clip(
            optimizer,
            loss,
            var_list=policy.q_func_vars,
            clip_val=policy.config["grad_clip"])
    else:
        grads_and_vars = optimizer.compute_gradients(
            loss, var_list=policy.q_func_vars)
    grads_and_vars = [(g, v) for (g, v) in grads_and_vars if g is not None]
    return grads_and_vars