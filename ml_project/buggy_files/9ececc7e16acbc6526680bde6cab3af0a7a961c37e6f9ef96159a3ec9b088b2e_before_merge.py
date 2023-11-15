def display_failures(results: TestResultSet) -> None:
    """Display all failures in the test run."""
    if not results.has_failures:
        return

    display_section_name("FAILURES")
    for result in results.results:
        if not result.has_failures:
            continue
        display_single_failure(result)