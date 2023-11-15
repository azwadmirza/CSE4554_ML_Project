def D_to_M_near_parabolic(D, ecc):
    x = (ecc - 1.0) / (ecc + 1.0) * (D ** 2)
    assert abs(x) < 1
    S = S_x(ecc, x)
    return (
        np.sqrt(2.0 / (1.0 + ecc)) * D + np.sqrt(2.0 / (1.0 + ecc) ** 3) * (D ** 3) * S
    )