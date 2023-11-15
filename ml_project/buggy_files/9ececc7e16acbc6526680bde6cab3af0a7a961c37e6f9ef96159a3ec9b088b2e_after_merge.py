def display_failures(results: TestResultSet) -> None:
    """Display all failures in the test run."""
    if not results.has_failures:
        return
    relevant_results = [result for result in results if not result.is_errored]
    if not relevant_results:
        return
    display_section_name("FAILURES")
    for result in relevant_results:
        if not result.has_failures:
            continue
        display_single_failure(result)