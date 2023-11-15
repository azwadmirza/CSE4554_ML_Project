def format_parameter(element):
    """
    Formats a particular parameter. Essentially the same as built-in formatting except using 'i' instead of 'j' for
    the imaginary number.

    :param element: {int, float, long, complex, Slot} Formats a parameter for Quil output.
    """
    if isinstance(element, integer_types) or isinstance(element, np.int_):
        return repr(element)
    elif isinstance(element, float):
        return check_for_pi(element)
    elif isinstance(element, complex):
        r = element.real
        i = element.imag
        if i < 0:
            return repr(r) + "-" + repr(abs(i)) + "i"
        else:
            return repr(r) + "+" + repr(i) + "i"
    elif isinstance(element, Slot):
        return format_parameter(element.value())
    assert False, "Invalid parameter: %r" % element