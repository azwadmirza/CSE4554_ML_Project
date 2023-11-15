def relu_deriv(a_sh):
    """
    Compute the derivative of Relu

    Args:
        a_sh (AdditiveSharingTensor): the private tensor on which the op applies

    Returns:
        0 if Dec(a_sh) < 0
        1 if Dec(a_sh) > 0
        encrypted in an AdditiveSharingTensor
    """
    assert (
        a_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    workers = a_sh.locations
    crypto_provider = a_sh.crypto_provider
    L = a_sh.field
    dtype = get_dtype(L)
    # Common randomness
    u = _shares_of_zero(1, L, dtype, crypto_provider, *workers)

    # 1)
    y_sh = a_sh * 2

    # 2) Not applicable with algebraic shares
    y_sh = share_convert(y_sh)

    # 3)
    alpha_sh = msb(y_sh)

    # 4)
    j = sy.MultiPointerTensor(
        children=[torch.tensor([int(i == 0)]).send(w, **no_wrap) for i, w in enumerate(workers)]
    )
    gamma_sh = j - alpha_sh + u
    return gamma_sh