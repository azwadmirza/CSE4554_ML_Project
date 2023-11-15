async def setup_pex_cli_process(
    request: PexCliProcess,
    pex_binary: PexBinary,
    pex_env: PexEnvironment,
    python_native_code: PythonNativeCode,
) -> Process:
    tmpdir = ".tmp"
    downloaded_pex_bin, tmp_dir_digest = await MultiGet(
        Get(DownloadedExternalTool, ExternalToolRequest, pex_binary.get_request(Platform.current)),
        # TODO(John Sirois): Use a Directory instead of this FileContent hack when a fix for
        #  https://github.com/pantsbuild/pants/issues/9650 lands.
        Get(Digest, CreateDigest([FileContent(f"{tmpdir}/.reserve", b"")])),
    )

    digests_to_merge = [downloaded_pex_bin.digest, tmp_dir_digest]
    if request.additional_input_digest:
        digests_to_merge.append(request.additional_input_digest)
    input_digest = await Get(Digest, MergeDigests(digests_to_merge))

    pex_root_path = ".cache/pex_root"
    argv = pex_env.create_argv(
        downloaded_pex_bin.exe, *request.argv, "--pex-root", pex_root_path, python=request.python
    )
    env = {
        # Ensure Pex and its subprocesses create temporary files in the the process execution
        # sandbox. It may make sense to do this generally for Processes, but in the short term we
        # have known use cases where /tmp is too small to hold large wheel downloads Pex is asked to
        # perform. Making the TMPDIR local to the sandbox allows control via
        # --local-execution-root-dir for the local case and should work well with remote cases where
        # a remoting implementation has to allow for processes producing large binaries in a
        # sandbox to support reasonable workloads.
        "TMPDIR": tmpdir,
        **pex_env.environment_dict,
        **python_native_code.environment_dict,
        **(request.extra_env or {}),
    }

    return Process(
        argv,
        description=request.description,
        input_digest=input_digest,
        env=env,
        output_files=request.output_files,
        output_directories=request.output_directories,
        append_only_caches={"pex_root": pex_root_path},
    )