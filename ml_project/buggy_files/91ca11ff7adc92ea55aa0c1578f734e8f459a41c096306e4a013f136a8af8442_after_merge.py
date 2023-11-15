def read_cle_release_file():
    """Read the CLE release file and return a dict with its attributes.

    This file is present on newer versions of Cray.

    The release file looks something like this::

        RELEASE=6.0.UP07
        BUILD=6.0.7424
        ...

    The dictionary we produce looks like this::

        {
          "RELEASE": "6.0.UP07",
          "BUILD": "6.0.7424",
          ...
        }

    Returns:
        dict: dictionary of release attributes
    """
    with open(_cle_release_file) as release_file:
        result = {}
        for line in release_file:
            # use partition instead of split() to ensure we only split on
            # the first '=' in the line.
            key, _, value = line.partition('=')
            result[key] = value.strip()
        return result