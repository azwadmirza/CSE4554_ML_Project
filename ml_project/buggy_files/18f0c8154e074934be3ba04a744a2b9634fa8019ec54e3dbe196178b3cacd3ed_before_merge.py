def sort_stream(
    input_stream: TextIO,
    output_stream: TextIO,
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = False,
    **config_kwargs,
):
    """Sorts any imports within the provided code stream, outputs to the provided output stream.
    Directly returns nothing.

    - **input_stream**: The stream of code with imports that need to be sorted.
    - **output_stream**: The stream where sorted imports should be written to.
    - **extension**: The file extension that contains imports. Defaults to filename extension or py.
    - **config**: The config object to use when sorting imports.
    - **file_path**: The disk location where the code string was pulled from.
    - **disregard_skip**: set to `True` if you want to ignore a skip set in config for this file.
    - ****config_kwargs**: Any config modifications.
    """
    config = _config(path=file_path, config=config, **config_kwargs)
    content_source = str(file_path or "Passed in content")
    if not disregard_skip:
        if file_path and config.is_skipped(file_path):
            raise FileSkipSetting(content_source)

    _internal_output = output_stream

    if config.atomic:
        try:
            file_content = input_stream.read()
            compile(file_content, content_source, "exec", 0, 1)
            input_stream = StringIO(file_content)
        except SyntaxError:
            raise ExistingSyntaxErrors(content_source)

        if not output_stream.readable():
            _internal_output = StringIO()

    try:
        changed = _sort_imports(
            input_stream,
            _internal_output,
            extension=extension or (file_path and file_path.suffix.lstrip(".")) or "py",
            config=config,
        )
    except FileSkipComment:
        raise FileSkipComment(content_source)

    if config.atomic:
        _internal_output.seek(0)
        try:
            compile(_internal_output.read(), content_source, "exec", 0, 1)
            _internal_output.seek(0)
            if _internal_output != output_stream:
                output_stream.write(_internal_output.read())
        except SyntaxError:  # pragma: no cover
            raise IntroducedSyntaxErrors(content_source)

    return changed