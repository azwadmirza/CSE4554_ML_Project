def execute_from_schema(
    schema: BaseSchema,
    base_url: str,
    checks: Iterable[Callable],
    *,
    hypothesis_options: Optional[Dict[str, Any]] = None,
    auth: Optional[Auth] = None,
    headers: Optional[Dict[str, Any]] = None,
) -> Generator[events.ExecutionEvent, None, None]:
    """Execute tests for the given schema.

    Provides the main testing loop and preparation step.
    """
    results = TestResultSet()

    with get_session(auth, headers) as session:
        settings = get_hypothesis_settings(hypothesis_options)

        yield events.Initialized(results=results, schema=schema, checks=checks, hypothesis_settings=settings)

        for endpoint, test in schema.get_all_tests(single_test, settings):
            result = TestResult(path=endpoint.path, method=endpoint.method)
            yield events.BeforeExecution(results=results, schema=schema, endpoint=endpoint)
            try:
                if isinstance(test, InvalidSchema):
                    status = Status.error
                    result.add_error(test)
                else:
                    test(session, base_url, checks, result)
                    status = Status.success
            except AssertionError:
                status = Status.failure
            except hypothesis.errors.Flaky:
                status = Status.error
                result.mark_errored()
                flaky_example = result.checks[-1].example
                result.add_error(
                    hypothesis.errors.Flaky(
                        "Tests on this endpoint produce unreliable results: \n"
                        "Falsified on the first call but did not on a subsequent one"
                    ),
                    flaky_example,
                )
            except hypothesis.errors.Unsatisfiable:
                # We need more clear error message here
                status = Status.error
                result.add_error(
                    hypothesis.errors.Unsatisfiable("Unable to satisfy schema parameters for this endpoint")
                )
            except Exception as error:
                status = Status.error
                result.add_error(error)
            results.append(result)
            yield events.AfterExecution(results=results, schema=schema, endpoint=endpoint, status=status)

    yield events.Finished(results=results, schema=schema)