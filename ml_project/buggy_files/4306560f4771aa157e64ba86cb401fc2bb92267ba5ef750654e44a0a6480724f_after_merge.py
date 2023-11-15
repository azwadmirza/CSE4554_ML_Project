def matches_requirement(req, wheels):
    """List of wheels matching a requirement.

    :param req: The requirement to satisfy
    :param wheels: List of wheels to search.
    """
    try:
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from pkg_resources import Distribution, Requirement  # vendor:skip
        else:
          from pex.third_party.pkg_resources import Distribution, Requirement

    except ImportError:
        raise RuntimeError("Cannot use requirements without pkg_resources")

    req = Requirement.parse(req)

    selected = []
    for wf in wheels:
        f = wf.parsed_filename
        dist = Distribution(project_name=f.group("name"), version=f.group("ver"))
        if dist in req:
            selected.append(wf)
    return selected