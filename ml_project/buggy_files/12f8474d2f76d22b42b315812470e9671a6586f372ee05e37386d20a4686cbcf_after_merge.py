def _get_var_parent(name):
    """Get parent of the variable given its name
    """
    # If not a temporary variable
    if not name.startswith('$'):
        # Return the base component of the name
        return name.split('.', )[0]