def maxpool(x_sh):
    """ Compute MaxPool: returns fresh shares of the max value in the input tensor
    and the index of this value in the flattened tensor

    Args:
        x_sh (AdditiveSharingTensor): the private tensor on which the op applies

    Returns:
        maximum value as an AdditiveSharingTensor
        index of this value in the flattened tensor as an AdditiveSharingTensor
    """
    assert (
        x_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    if x_sh.is_wrapper:
        x_sh = x_sh.child
    alice, bob = x_sh.locations
    crypto_provider = x_sh.crypto_provider
    L = x_sh.field
    dtype = get_dtype(L)

    x_sh = x_sh.contiguous().view(-1)

    # Common Randomness
    u_sh = _shares_of_zero(1, L, dtype, crypto_provider, alice, bob)
    v_sh = _shares_of_zero(1, L, dtype, crypto_provider, alice, bob)

    # 1)
    max_sh = x_sh[0]
    ind_sh = torch.tensor([0]).share(
        alice, bob, field=L, dtype=dtype, crypto_provider=crypto_provider, **no_wrap
    )  # I did not manage to create an AST with 0 and 0 as shares

    for i in range(1, len(x_sh)):
        # 3)
        w_sh = x_sh[i] - max_sh

        # 4)
        beta_sh = relu_deriv(w_sh)

        # 5)
        max_sh = select_share(beta_sh, max_sh, x_sh[i])

        # 6)
        k = torch.tensor([i]).share(
            alice, bob, field=L, dtype=dtype, crypto_provider=crypto_provider, **no_wrap
        )  # I did not manage to create an AST with 0 and i as shares

        # 7)
        ind_sh = select_share(beta_sh, ind_sh, k)

    return max_sh + u_sh, ind_sh + v_sh