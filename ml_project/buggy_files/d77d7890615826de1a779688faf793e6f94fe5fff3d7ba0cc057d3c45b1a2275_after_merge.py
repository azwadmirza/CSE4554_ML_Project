    def wavelength_match(a, b):
        """Return if two wavelengths are equal.

        Args:
            a (tuple or scalar): (min wl, nominal wl, max wl) or scalar wl
            b (tuple or scalar): (min wl, nominal wl, max wl) or scalar wl
        """
        if type(a) == (type(b) or
                       isinstance(a, numbers.Number) and
                       isinstance(b, numbers.Number)):
            return a == b
        elif a is None or b is None:
            return False
        elif isinstance(a, (list, tuple)) and len(a) == 3:
            return a[0] <= b <= a[2]
        elif isinstance(b, (list, tuple)) and len(b) == 3:
            return b[0] <= a <= b[2]
        else:
            raise ValueError("Can only compare wavelengths of length 1 or 3")