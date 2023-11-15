def _mark_xfail_checks(estimator, check, pytest):
    """Mark estimator check pairs with xfail"""
    if isinstance(estimator, type):
        # try to construct estimator to get tags, if it is unable to then
        # return the estimator class
        try:
            xfail_checks = _safe_tags(_construct_instance(estimator),
                                      '_xfail_test')
        except Exception:
            return estimator, check
    else:
        xfail_checks = _safe_tags(estimator, '_xfail_test')

    if not xfail_checks:
        return estimator, check

    check_name = _set_check_estimator_ids(check)
    msg = xfail_checks.get(check_name, None)

    if msg is None:
        return estimator, check

    return pytest.param(
        estimator, check, marks=pytest.mark.xfail(reason=msg))