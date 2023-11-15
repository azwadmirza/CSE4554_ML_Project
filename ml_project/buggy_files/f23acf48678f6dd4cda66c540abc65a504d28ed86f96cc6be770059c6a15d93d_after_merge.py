def logsumexp(x, axis=None, keepdims=True):
    # Adapted from https://github.com/Theano/Theano/issues/1563
    x_max = tt.max(x, axis=axis, keepdims=True)
    res = tt.log(tt.sum(tt.exp(x - x_max), axis=axis, keepdims=True)) + x_max
    return res if keepdims else res.squeeze()