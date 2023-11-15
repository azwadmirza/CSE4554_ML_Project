def msb(a_sh):
    """
    Compute the most significant bit in a_sh, this is an implementation of the
    SecureNN paper https://eprint.iacr.org/2018/442.pdf

    Args:
        a_sh (AdditiveSharingTensor): the tensor of study
    Return:
        the most significant bit
    """

    alice, bob = a_sh.locations
    crypto_provider = a_sh.crypto_provider
    L = a_sh.field + 1  # field of a is L - 1
    dtype = get_dtype(L)
    input_shape = a_sh.shape
    a_sh = a_sh.view(-1)

    # the commented out numbers below correspond to the
    # line numbers in Table 5 of the SecureNN paper
    # https://eprint.iacr.org/2018/442.pdf

    # Common Randomness
    beta = _random_common_bit(alice, bob)
    u = _shares_of_zero(1, L, dtype, crypto_provider, alice, bob)

    # 1)
    x = torch.tensor(a_sh.shape).random_(get_max_val_field(L - 1))
    x_bit = decompose(x, L)
    x_sh = x.share(
        bob, alice, field=L - 1, dtype="custom", crypto_provider=crypto_provider, **no_wrap
    )
    x_bit_0 = x_bit[..., 0]
    x_bit_sh_0 = x_bit_0.share(bob, alice, field=L, crypto_provider=crypto_provider, **no_wrap)
    x_bit_sh = x_bit.share(
        bob, alice, field=p, dtype="custom", crypto_provider=crypto_provider, **no_wrap
    )

    # 2)
    y_sh = a_sh * 2
    r_sh = y_sh + x_sh

    # 3)
    r = r_sh.reconstruct()  # convert an additive sharing in multi pointer Tensor
    r_0 = decompose(r, L)[..., 0]

    # 4)
    beta_prime = private_compare(x_bit_sh, r, beta, L)

    # 5)
    beta_prime_sh = beta_prime.share(
        bob, alice, field=L, dtype=dtype, crypto_provider=crypto_provider, **no_wrap
    )

    # 7)
    j = sy.MultiPointerTensor(
        children=[torch.tensor([0]).send(alice, **no_wrap), torch.tensor([1]).send(bob, **no_wrap)]
    )
    gamma = beta_prime_sh + (j * beta) - (2 * beta * beta_prime_sh)

    # 8)
    delta = x_bit_sh_0 + (j * r_0) - (2 * r_0 * x_bit_sh_0)

    # 9)
    theta = gamma * delta

    # 10)
    a = gamma + delta - (theta * 2) + u

    if len(input_shape):
        return a.view(*list(input_shape))
    else:
        return a