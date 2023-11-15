def share_convert(a_sh):
    """
    Convert shares of a in field L to shares of a in field L - 1

    Args:
        a_sh (AdditiveSharingTensor): the additive sharing tensor who owns
            the shares in field L to convert

    Return:
        An additive sharing tensor with shares in field L-1
    """
    assert isinstance(a_sh, sy.AdditiveSharingTensor)
    assert (
        a_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"

    workers = a_sh.locations
    crypto_provider = a_sh.crypto_provider
    L = a_sh.field
    # torch_dtype = get_torch_dtype(L)
    # dtype = get_dtype(L)
    # Common randomness
    # eta_pp = _random_common_bit(*workers)
    # r = _random_common_value(L, *workers)

    # Share remotely r
    # r_sh = (
    #    (r * 1)
    #    .child[workers[0].id]
    #    .share(*workers, field=L, dtype=dtype, crypto_provider=crypto_provider)
    #    .get()
    #    .child
    # )
    # r_shares = r_sh.child

    # WORKS WITH N PARTIES, NEEDS BUGFIXING IN WRAP
    # alpha0 = wrap(r_sh, L)
    # alphas = [alpha0.copy().move(w) for w in workers[1:]]
    # alpha = sy.MultiPointerTensor(children=[alpha0, *alphas])

    # WORKS WITH 2 PARTIES
    # alpha0 = (
    #    (
    #        (r_shares[workers[0].id] + r_shares[workers[1].id].copy().move(workers[0]))
    #        > get_max_val_field(L)
    #    )
    # ).type(torch_dtype)
    # alpha1 = alpha0.copy().move(workers[1])
    # alpha = sy.MultiPointerTensor(children=[alpha0, alpha1])

    u_sh = _shares_of_zero(1, L - 1, "custom", crypto_provider, *workers)

    # 2)
    # a_tilde_sh = a_sh + r_sh
    # a_shares = a_sh.child
    # beta0 = (
    #    ((a_shares[workers[0].id] + r_shares[workers[0].id]) > get_max_val_field(L))
    #    + ((a_shares[workers[0].id] + r_shares[workers[0].id]) < get_min_val_field(L))
    # ).type(torch_dtype)
    # beta1 = (
    #    ((a_shares[workers[1].id] + r_shares[workers[1].id]) > get_max_val_field(L))
    #    + ((a_shares[workers[1].id] + r_shares[workers[1].id]) < get_min_val_field(L))
    # ).type(torch_dtype)

    # beta = sy.MultiPointerTensor(children=[beta0, beta1])

    # 4)
    # a_tilde_shares = a_tilde_sh.child
    # delta = a_tilde_shares[workers[0].id].copy().get() + a_tilde_shares[workers[1].id].copy().get()
    # Check for both positive and negative overflows
    # delta = ((delta > get_max_val_field(L)) + (delta < get_min_val_field(L))).type(torch_dtype)
    # x = a_tilde_sh.get()

    # 5)
    # x_bit = decompose(x, L)
    # x_bit_sh = x_bit.share(
    #    *workers, field=p, dtype="custom", crypto_provider=crypto_provider, **no_wrap
    # )
    # delta_sh = delta.share(
    #    *workers, field=L - 1, dtype="custom", crypto_provider=crypto_provider, **no_wrap
    # )

    # 6)
    # eta_p = private_compare(x_bit_sh, r - 1, eta_pp, L)
    # 7)
    # eta_p_sh = eta_p.share(
    #    *workers, field=L - 1, dtype="custom", crypto_provider=crypto_provider, **no_wrap
    # )

    # 9)
    # j = sy.MultiPointerTensor(
    #    children=[
    #        torch.tensor([int(i != 0)]).send(w, **no_wrap)
    #        for i, w in enumerate(workers)
    #    ]
    # )
    # eta_sh = eta_p_sh + (1 - j) * eta_pp - 2 * eta_pp * eta_p_sh
    # 10)
    # theta_sh = beta - (1 - j) * (alpha + 1) + delta_sh + eta_sh
    # 11)
    # NOTE:
    # It seems simple operation with shares in L-1 field is enough to conver a_sh from L to L-1
    # Conversion of shares is handled internally in AST ops for custom dtype
    y_sh = u_sh + a_sh
    return y_sh