    def __new__(cls, real, imag=0, *args, **kwargs):
        if isinstance(real, string_types):
            value = super(HyComplex, cls).__new__(
                cls, strip_digit_separators(real)
            )
            p1, _, p2 = real.lstrip("+-").replace("-", "+").partition("+")
            check_inf_nan_cap(p1, value.imag if "j" in p1 else value.real)
            if p2:
                check_inf_nan_cap(p2, value.imag)
            return value
        return super(HyComplex, cls).__new__(cls, real, imag)