def Kuu_conv_patch(inducing_variable, kernel, jitter=0.0):
    return kernel.base_kernel.K(inducing_variable.Z) + jitter * tf.eye(
        inducing_variable.num_inducing, dtype=default_float()
    )