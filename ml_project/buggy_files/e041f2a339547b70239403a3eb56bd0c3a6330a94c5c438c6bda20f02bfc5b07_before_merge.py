def assert_string_list(dist, attr, value):
    """Verify that value is a string list"""
    try:
        assert ''.join(value) != value
    except (TypeError, ValueError, AttributeError, AssertionError):
        raise DistutilsSetupError(
            "%r must be a list of strings (got %r)" % (attr, value)
        )