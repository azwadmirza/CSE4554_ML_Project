def private_compare(x_bit_sh, r, beta, L):
    """
    Perform privately x > r

    args:
        x (AdditiveSharedTensor): the private tensor
        r (MultiPointerTensor): the threshold commonly held by alice and bob
        beta (MultiPointerTensor): a boolean commonly held by alice and bob to
            hide the result of computation for the crypto provider
        L(int): field size for r

    return:
        β′ = β ⊕ (x > r).
    """
    assert isinstance(x_bit_sh, sy.AdditiveSharingTensor)
    assert isinstance(r, sy.MultiPointerTensor)
    assert isinstance(beta, sy.MultiPointerTensor)
    # Would it be safer to have a different r/beta for each value in the tensor?

    alice, bob = x_bit_sh.locations
    crypto_provider = x_bit_sh.crypto_provider
    p = x_bit_sh.field

    # the commented out numbers below correspond to the
    # line numbers in Algorithm 3 of the SecureNN paper
    # https://eprint.iacr.org/2018/442.pdf

    # Common randomess
    s = torch.randint(1, p, x_bit_sh.shape).send(alice, bob, **no_wrap)
    u = torch.randint(1, p, x_bit_sh.shape).send(alice, bob, **no_wrap)
    perm = torch.randperm(x_bit_sh.shape[-1]).send(alice, bob, **no_wrap)

    j = sy.MultiPointerTensor(
        children=[torch.tensor([0]).send(alice, **no_wrap), torch.tensor([1]).send(bob, **no_wrap)]
    )

    # 1)
    t = r + 1
    t_bit = decompose(t, L)
    r_bit = decompose(r, L)

    # if beta == 0
    # 5)
    w = x_bit_sh + (j * r_bit) - (2 * r_bit * x_bit_sh)
    # 6)
    wc = w.flip(-1).cumsum(-1).flip(-1) - w
    c_beta0 = -x_bit_sh + (j * r_bit) + j + wc

    # elif beta == 1 AND r != 2^l- 1
    # 8)
    w = x_bit_sh + (j * t_bit) - (2 * t_bit * x_bit_sh)
    # 9)
    wc = w.flip(-1).cumsum(-1).flip(-1) - w
    c_beta1 = x_bit_sh + (-j * t_bit) + j + wc

    # else
    # 11)
    c_igt1 = (1 - j) * (u + 1) - (j * u)
    c_ie1 = (1 - 2 * j) * u

    l1_mask = torch.zeros(x_bit_sh.shape).long()
    l1_mask[..., 0] = 1
    l1_mask = l1_mask.send(alice, bob, **no_wrap)
    # c_else = if i == 1 c_ie1 else c_igt1
    c_else = (l1_mask * c_ie1) + ((1 - l1_mask) * c_igt1)

    # Mask for the case r == 2^l −1
    r_mask = (r == get_r_mask(L)).long()
    r_mask = r_mask.unsqueeze(-1)

    # Mask combination to execute the if / else statements of 4), 7), 10)
    c = (1 - beta) * c_beta0 + (beta * (1 - r_mask)) * c_beta1 + (beta * r_mask) * c_else

    # 14)
    # Hide c values
    mask = s * c

    # Permute the mask
    # I have to create idx because Ellipsis are still not supported
    # (I would like to do permuted_mask = mask[..., perm])
    idx = [slice(None)] * (len(x_bit_sh.shape) - 1) + [perm]
    permuted_mask = mask[idx]
    # Send it to another worker
    # We do this because we can't allow the local worker to get and see permuted_mask
    # because otherwise it can inverse the permutation and remove s to get c.
    # So opening the permuted_mask should be made by a worker which doesn't have access to the randomness
    remote_mask = permuted_mask.wrap().send(crypto_provider, **no_wrap)

    # 15)
    d_ptr = remote_mask.remote_get()
    beta_prime = (d_ptr == 0).sum(-1)

    # Get result back
    res = beta_prime.get()
    return res