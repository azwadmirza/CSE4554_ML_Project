def _interval_property(target_unit):
    return property(functools.partial(_to_unit, target_unit=target_unit))