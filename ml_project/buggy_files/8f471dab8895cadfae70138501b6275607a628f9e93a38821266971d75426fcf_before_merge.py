def Kuf_conv_patch(feat, kern, Xnew):
    Xp = kern.get_patches(Xnew)  # [N, num_patches, patch_len]
    bigKzx = kern.base_kernel.K(feat.Z, Xp)  # [M, N, P] -- thanks to broadcasting of kernels
    Kzx = tf.reduce_sum(bigKzx * kern.weights if hasattr(kern, "weights") else bigKzx, [2])
    return Kzx / kern.num_patches