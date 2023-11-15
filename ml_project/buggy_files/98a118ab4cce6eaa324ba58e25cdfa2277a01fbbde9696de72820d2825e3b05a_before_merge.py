def Kuu_conv_patch(feat, kern, jitter=0.0):
    return kern.base_kernel.K(feat.Z) + jitter * tf.eye(len(feat), dtype=default_float())