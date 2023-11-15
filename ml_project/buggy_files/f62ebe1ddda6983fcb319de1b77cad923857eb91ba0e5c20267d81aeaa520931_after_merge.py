def relu(a_sh):
    """
    Compute Relu

    Args:
        a_sh (AdditiveSharingTensor): the private tensor on which the op applies

    Returns:
        Dec(a_sh) > 0
        encrypted in an AdditiveSharingTensor
    """
    assert (
        a_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    workers = a_sh.locations
    crypto_provider = a_sh.crypto_provider
    L = a_sh.field
    dtype = get_dtype(L)
    # Common Randomness
    u = _shares_of_zero(1, L, dtype, crypto_provider, *workers)

    return a_sh * relu_deriv(a_sh) + u