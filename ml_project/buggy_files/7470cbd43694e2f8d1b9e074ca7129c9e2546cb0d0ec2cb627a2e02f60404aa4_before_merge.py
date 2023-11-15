async def create_pex(
    request: PexRequest,
    python_setup: PythonSetup,
    python_repos: PythonRepos,
    platform: Platform,
    pex_runtime_environment: PexRuntimeEnvironment,
) -> Pex:
    """Returns a PEX with the given settings."""

    argv = [
        "--output-file",
        request.output_filename,
        # NB: In setting `--no-pypi`, we rely on the default value of `--python-repos-indexes`
        # including PyPI, which will override `--no-pypi` and result in using PyPI in the default
        # case. Why set `--no-pypi`, then? We need to do this so that
        # `--python-repos-repos=['custom_url']` will only point to that index and not include PyPI.
        "--no-pypi",
        *(f"--index={index}" for index in python_repos.indexes),
        *(f"--repo={repo}" for repo in python_repos.repos),
        *request.additional_args,
    ]

    if request.internal_only:
        # This will result in a faster build, but worse compatibility at runtime.
        argv.append("--use-first-matching-interpreter")

    # NB: If `--platform` is specified, this signals that the PEX should not be built locally.
    # `--interpreter-constraint` only makes sense in the context of building locally. These two
    # flags are mutually exclusive. See https://github.com/pantsbuild/pex/issues/957.
    if request.platforms:
        # TODO(#9560): consider validating that these platforms are valid with the interpreter
        #  constraints.
        argv.extend(request.platforms.generate_pex_arg_list())
    else:
        argv.extend(request.interpreter_constraints.generate_pex_arg_list())

    argv.append("--no-emit-warnings")
    verbosity = pex_runtime_environment.verbosity
    if verbosity > 0:
        argv.append(f"-{'v' * verbosity}")

    if python_setup.resolver_jobs:
        argv.extend(["--jobs", str(python_setup.resolver_jobs)])

    if python_setup.manylinux:
        argv.extend(["--manylinux", python_setup.manylinux])
    else:
        argv.append("--no-manylinux")

    if request.entry_point is not None:
        argv.extend(["--entry-point", request.entry_point])

    if python_setup.requirement_constraints is not None:
        argv.extend(["--constraints", python_setup.requirement_constraints])

    source_dir_name = "source_files"
    argv.append(f"--sources-directory={source_dir_name}")

    argv.extend(request.requirements)

    constraint_file_digest = EMPTY_DIGEST
    if python_setup.requirement_constraints is not None:
        constraint_file_digest = await Get(
            Digest,
            PathGlobs(
                [python_setup.requirement_constraints],
                glob_match_error_behavior=GlobMatchErrorBehavior.error,
                conjunction=GlobExpansionConjunction.all_match,
                description_of_origin="the option `--python-setup-requirement-constraints`",
            ),
        )

    sources_digest_as_subdir = await Get(
        Digest, AddPrefix(request.sources or EMPTY_DIGEST, source_dir_name)
    )
    additional_inputs_digest = request.additional_inputs or EMPTY_DIGEST

    merged_digest = await Get(
        Digest,
        MergeDigests(
            (
                sources_digest_as_subdir,
                additional_inputs_digest,
                constraint_file_digest,
            )
        ),
    )

    description = request.description
    if description is None:
        if request.requirements:
            description = (
                f"Building {request.output_filename} with "
                f"{pluralize(len(request.requirements), 'requirement')}: "
                f"{', '.join(request.requirements)}"
            )
        else:
            description = f"Building {request.output_filename}"

    process = await Get(
        Process,
        PexCliProcess(
            argv=argv,
            additional_input_digest=merged_digest,
            description=description,
            output_files=[request.output_filename],
        ),
    )

    # NB: Building a Pex is platform dependent, so in order to get a PEX that we can use locally
    # without cross-building, we specify that our PEX command should be run on the current local
    # platform.
    result = await Get(
        ProcessResult,
        MultiPlatformProcess(
            {(PlatformConstraint(platform.value), PlatformConstraint(platform.value)): process}
        ),
    )

    if verbosity > 0:
        log_output = result.stderr.decode()
        if log_output:
            logger.info("%s", log_output)

    return Pex(
        digest=result.output_digest,
        name=request.output_filename,
        internal_only=request.internal_only,
    )