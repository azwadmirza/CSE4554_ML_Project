def build_empty_error_execution(image_obj, tag, bundle, errors=None, warnings=None):
    """
    Creates an empty BundleExecution suitable for use in error cases where the bundle was not actually run but this object
    is needed to populate errors and warnings for return.

    :param image_obj:
    :param tag:
    :param bundle:
    :return: BundleExecution object with bundle, image, and tag set and a STOP final action.
    """

    b = BundleExecution(bundle=bundle, image_id=image_obj.id, tag=tag)
    b.bundle_decision = BundleDecision(policy_decision=FailurePolicyDecision())
    b.errors = errors
    b.warnings = warnings
    return b