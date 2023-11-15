def _format_checks(checks_dict):
    if checks_dict is None:
        return "None"

    checks = []
    for check_name, check_kwargs in checks_dict.items():
        if check_kwargs is None:
            warnings.warn(f"Check {check_name} cannot be serialized. This check will be ignored")
        else:
            args = ", ".join(
                "{}={}".format(k, v.__repr__()) for k, v in check_kwargs.items()
            )
            checks.append("Check.{}({})".format(check_name, args))
    return "[{}]".format(', '.join(checks))