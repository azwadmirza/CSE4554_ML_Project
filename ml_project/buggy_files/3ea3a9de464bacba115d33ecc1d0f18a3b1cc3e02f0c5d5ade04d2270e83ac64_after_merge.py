    def basepython_default(testenv_config, value):
        """either user set or proposed from the factor name

        in both cases we check that the factor name implied python version and the resolved
        python interpreter version match up; if they don't we warn, unless ignore base
        python conflict is set in which case the factor name implied version if forced
        """
        for factor in testenv_config.factors:
            if factor in tox.PYTHON.DEFAULT_FACTORS:
                implied_python = tox.PYTHON.DEFAULT_FACTORS[factor]
                break
        else:
            implied_python, factor = None, None

        if testenv_config.config.ignore_basepython_conflict and implied_python is not None:
            return implied_python

        proposed_python = (implied_python or sys.executable) if value is None else str(value)
        if implied_python is not None and implied_python != proposed_python:
            testenv_config.basepython = proposed_python
            match = tox.PYTHON.PY_FACTORS_RE.match(factor)
            implied_version = match.group(2) if match else None
            if implied_version is not None:
                python_info_for_proposed = testenv_config.python_info
                if not isinstance(python_info_for_proposed, NoInterpreterInfo):
                    proposed_version = "".join(
                        str(i) for i in python_info_for_proposed.version_info[0:2]
                    )
                    # '27'.startswith('2') or '27'.startswith('27')
                    if not proposed_version.startswith(implied_version):
                        # TODO(stephenfin): Raise an exception here in tox 4.0
                        warnings.warn(
                            "conflicting basepython version (set {}, should be {}) for env '{}';"
                            "resolve conflict or set ignore_basepython_conflict".format(
                                proposed_version, implied_version, testenv_config.envname
                            )
                        )
        return proposed_python