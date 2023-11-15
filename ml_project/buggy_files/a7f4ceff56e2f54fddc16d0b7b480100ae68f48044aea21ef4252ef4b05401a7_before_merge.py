def reshape_sampled(sampled, size, dist_shape):
    dist_shape = infer_shape(dist_shape)
    repeat_shape = infer_shape(size)
    return np.reshape(sampled, repeat_shape + dist_shape)