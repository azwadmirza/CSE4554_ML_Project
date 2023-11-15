def display_errors(results: TestResultSet) -> None:
    """Display all errors in the test run."""
    if not results.has_errors:
        return

    display_section_name("ERRORS")
    for result in results.results:
        if not result.has_errors:
            continue
        display_single_error(result)