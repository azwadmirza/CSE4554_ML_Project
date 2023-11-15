def main(
    ctx: click.Context,
    code: Optional[str],
    line_length: int,
    target_version: List[TargetVersion],
    check: bool,
    diff: bool,
    fast: bool,
    pyi: bool,
    py36: bool,
    skip_string_normalization: bool,
    quiet: bool,
    verbose: bool,
    include: str,
    exclude: str,
    src: Tuple[str],
    config: Optional[str],
) -> None:
    """The uncompromising code formatter."""
    write_back = WriteBack.from_configuration(check=check, diff=diff)
    if target_version:
        if py36:
            err(f"Cannot use both --target-version and --py36")
            ctx.exit(2)
        else:
            versions = set(target_version)
    elif py36:
        err(
            "--py36 is deprecated and will be removed in a future version. "
            "Use --target-version py36 instead."
        )
        versions = PY36_VERSIONS
    else:
        # We'll autodetect later.
        versions = set()
    mode = FileMode(
        target_versions=versions,
        line_length=line_length,
        is_pyi=pyi,
        string_normalization=not skip_string_normalization,
    )
    if config and verbose:
        out(f"Using configuration from {config}.", bold=False, fg="blue")
    if code is not None:
        print(format_str(code, mode=mode))
        ctx.exit(0)
    try:
        include_regex = re_compile_maybe_verbose(include)
    except re.error:
        err(f"Invalid regular expression for include given: {include!r}")
        ctx.exit(2)
    try:
        exclude_regex = re_compile_maybe_verbose(exclude)
    except re.error:
        err(f"Invalid regular expression for exclude given: {exclude!r}")
        ctx.exit(2)
    report = Report(check=check, quiet=quiet, verbose=verbose)
    root = find_project_root(src)
    sources: Set[Path] = set()
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.update(
                gen_python_files_in_dir(p, root, include_regex, exclude_regex, report)
            )
        elif p.is_file() or s == "-":
            # if a file was explicitly given, we don't care about its extension
            sources.add(p)
        else:
            err(f"invalid path: {s}")
    if len(sources) == 0:
        if verbose or not quiet:
            out("No paths given. Nothing to do 😴")
        ctx.exit(0)

    if len(sources) == 1:
        reformat_one(
            src=sources.pop(),
            fast=fast,
            write_back=write_back,
            mode=mode,
            report=report,
        )
    else:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        try:
            loop.run_until_complete(
                schedule_formatting(
                    sources=sources,
                    fast=fast,
                    write_back=write_back,
                    mode=mode,
                    report=report,
                    loop=loop,
                    executor=executor,
                )
            )
        finally:
            shutdown(loop)
    if verbose or not quiet:
        bang = "💥 💔 💥" if report.return_code else "✨ 🍰 ✨"
        out(f"All done! {bang}")
        click.secho(str(report), err=True)
    ctx.exit(report.return_code)