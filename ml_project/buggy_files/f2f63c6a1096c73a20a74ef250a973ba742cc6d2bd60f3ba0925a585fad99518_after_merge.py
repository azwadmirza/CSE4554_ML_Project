def _interval_property(target_unit, name):
    return property(
        functools.partial(_to_unit, target_unit=target_unit),
        doc="""Extract the number of {0}s from an IntervalValue expression.

Returns
-------
IntegerValue
    The number of {0}s in the expression
""".format(name))