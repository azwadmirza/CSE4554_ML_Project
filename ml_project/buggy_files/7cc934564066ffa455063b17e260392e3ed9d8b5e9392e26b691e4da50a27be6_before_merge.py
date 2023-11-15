def maxpool_deriv(x_sh):
    """ Compute derivative of MaxPool

    Args:
        x_sh (AdditiveSharingTensor): the private tensor on which the op applies

    Returns:
        an AdditiveSharingTensor of the same shape as x_sh full of zeros except for
        a 1 at the position of the max value
    """
    assert (
        x_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    alice, bob = x_sh.locations
    crypto_provider = x_sh.crypto_provider
    L = x_sh.field
    dtype = get_dtype(L)
    torch_dtype = get_torch_dtype(L)

    n1, n2 = x_sh.shape
    n = n1 * n2
    x_sh = x_sh.view(-1)

    # Common Randomness
    U_sh = _shares_of_zero(n, L, dtype, crypto_provider, alice, bob)

    r = _random_common_value(L, alice, bob)

    # 1)
    _, ind_max_sh = maxpool(x_sh)

    # 2)
    j = sy.MultiPointerTensor(
        children=[torch.tensor([1]).send(alice, **no_wrap), torch.tensor([0]).send(bob, **no_wrap)]
    )
    k_sh = ind_max_sh + j * r

    # 3)
    t = k_sh.get()
    k = t % n
    E_k = torch.zeros(n, dtype=torch_dtype)
    E_k[k] = 1
    E_sh = E_k.share(alice, bob, field=L, dtype=dtype, **no_wrap)

    # 4)
    g = r % n
    D_sh = torch.roll(E_sh, -g)

    maxpool_d_sh = D_sh + U_sh
    return maxpool_d_sh.view(n1, n2)