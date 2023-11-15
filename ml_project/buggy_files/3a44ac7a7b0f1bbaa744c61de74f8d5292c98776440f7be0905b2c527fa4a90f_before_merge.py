def division(x_sh, y_sh, bit_len_max=None):
    """ Performs division of encrypted numbers

    Args:
        x_sh, y_sh (AdditiveSharingTensor): the private tensors on which the op applies

    Returns:
        element-wise integer division of x_sh by y_sh
    """
    assert (
        x_sh.dtype == y_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"
    alice, bob = x_sh.locations
    crypto_provider = x_sh.crypto_provider
    L = x_sh.field
    dtype = get_dtype(L)
    if bit_len_max is None:
        bit_len_max = Q_BITS(L) // 2

    x_shape = x_sh.shape
    y_shape = y_sh.shape
    assert x_shape == y_shape or list(y_shape) == [1]

    x_sh = x_sh.view(-1)
    y_sh = y_sh.view(-1)

    # Common Randomness
    w_sh = _shares_of_zero(bit_len_max, L, dtype, crypto_provider, alice, bob)
    s_sh = _shares_of_zero(1, L, dtype, crypto_provider, alice, bob)
    u_sh = _shares_of_zero(1, L, dtype, crypto_provider, alice, bob)

    ks = []
    for i in range(bit_len_max - 1, -1, -1):
        # 3)
        z_sh = x_sh - u_sh - 2 ** i * y_sh + w_sh[i]

        # 4)
        beta_sh = relu_deriv(z_sh)

        # 5)
        v_sh = beta_sh * (2 ** i * y_sh)

        # 6)
        k_sh = beta_sh * 2 ** i
        ks.append(k_sh)

        # 7)
        u_sh = u_sh + v_sh

    # 9)
    q = sum(ks) + s_sh

    if len(x_shape):
        return q.view(*x_shape)
    else:
        return q