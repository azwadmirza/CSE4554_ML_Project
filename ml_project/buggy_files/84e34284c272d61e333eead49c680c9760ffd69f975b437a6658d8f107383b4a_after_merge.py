def clip_gradients(policy: Policy, optimizer: "tf.keras.optimizers.Optimizer",
                   loss: TensorType) -> ModelGradients:
    return minimize_and_clip(
        optimizer,
        loss,
        var_list=policy.q_func_vars,
        clip_val=policy.config["grad_clip"])