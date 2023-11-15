def display_single_failure(result: TestResult) -> None:
    """Display a failure for a single method / endpoint."""
    display_subsection(result)
    for check in reversed(result.checks):
        if check.example is not None:
            output = {
                make_verbose_name(attribute): getattr(check.example, attribute.name)
                for attribute in Case.__attrs_attrs__  # type: ignore
                if attribute.name not in ("path", "method", "base_url")
            }
            max_length = max(map(len, output))
            template = f"{{:<{max_length}}} : {{}}"
            click.secho(template.format("Check", check.name), fg="red")
            for key, value in output.items():
                if (key == "Body" and value is not None) or value not in (None, {}):
                    click.secho(template.format(key, value), fg="red")
            # Display only the latest case
            # (dd): It is possible to find multiple errors, but the simplest option for now is to display
            # the latest and avoid deduplication, which will be done in the future.
            break