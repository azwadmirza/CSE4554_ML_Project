def install_req_from_req_string(
    req_string,  # type: str
    comes_from=None,  # type: Optional[InstallRequirement]
    isolated=False,  # type: bool
    wheel_cache=None,  # type: Optional[WheelCache]
    use_pep517=None  # type: Optional[bool]
):
    # type: (...) -> InstallRequirement
    try:
        req = Requirement(req_string)
    except InvalidRequirement:
        raise InstallationError("Invalid requirement: '%s'" % req)

    domains_not_allowed = [
        PyPI.file_storage_domain,
        TestPyPI.file_storage_domain,
    ]
    if (req.url and comes_from and comes_from.link and
            comes_from.link.netloc in domains_not_allowed):
        # Explicitly disallow pypi packages that depend on external urls
        raise InstallationError(
            "Packages installed from PyPI cannot depend on packages "
            "which are not also hosted on PyPI.\n"
            "%s depends on %s " % (comes_from.name, req)
        )

    return InstallRequirement(
        req, comes_from, isolated=isolated, wheel_cache=wheel_cache,
        use_pep517=use_pep517
    )