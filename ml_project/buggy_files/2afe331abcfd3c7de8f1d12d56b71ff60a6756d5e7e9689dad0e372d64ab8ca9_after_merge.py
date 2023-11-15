def select_share(alpha_sh, x_sh, y_sh):
    """ Performs select share protocol
    If the bit alpha_sh is 0, x_sh is returned
    If the bit alpha_sh is 1, y_sh is returned

    Args:
        x_sh (AdditiveSharingTensor): the first share to select
        y_sh (AdditiveSharingTensor): the second share to select
        alpha_sh (AdditiveSharingTensor): the bit to choose between x_sh and y_sh

    Return:
        z_sh = (1 - alpha_sh) * x_sh + alpha_sh * y_sh
    """
    assert (
        alpha_sh.dtype == x_sh.dtype == y_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    workers = alpha_sh.locations
    crypto_provider = alpha_sh.crypto_provider
    L = alpha_sh.field
    dtype = get_dtype(L)
    u_sh = _shares_of_zero(1, L, dtype, crypto_provider, *workers)

    # 1)
    w_sh = y_sh - x_sh

    # 2)
    c_sh = alpha_sh * w_sh

    # 3)
    z_sh = x_sh + c_sh + u_sh

    return z_sh