def display_single_failure(result: TestResult) -> None:
    """Display a failure for a single method / endpoint."""
    display_subsection(result)
    for check in reversed(result.checks):
        if check.example is not None:
            display_example(check.example, check.name)
            # Display only the latest case
            # (dd): It is possible to find multiple errors, but the simplest option for now is to display
            # the latest and avoid deduplication, which will be done in the future.
            break