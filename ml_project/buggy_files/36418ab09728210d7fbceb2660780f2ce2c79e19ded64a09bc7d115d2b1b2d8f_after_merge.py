def to_angstrom(value, unit):
    """Given a value with a unit (given in a string), convert to angstroms"""
    value_quantity = value * units.Unit(unit)
    return value_quantity.to(units.angstrom, equivalencies=units.spectral()).value