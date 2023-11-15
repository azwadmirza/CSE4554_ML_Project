def display_single_error(result: TestResult) -> None:
    display_subsection(result)
    for error, example in result.errors:
        message = "".join(traceback.format_exception_only(type(error), error))
        click.secho(message, fg="red")
        if example is not None:
            display_example(example)