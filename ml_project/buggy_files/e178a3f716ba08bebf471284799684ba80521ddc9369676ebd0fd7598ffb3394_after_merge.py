def validate_specifiers(instance, attr_, value):
    from packaging.specifiers import SpecifierSet, InvalidSpecifier
    if value == "":
        return True
    try:
        SpecifierSet(value)
    except (InvalidMarker, InvalidSpecifier):
        raise ValueError("Invalid Specifiers {0}".format(value))