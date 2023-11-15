async def find_binary(request: BinaryPathRequest) -> BinaryPaths:
    # TODO(John Sirois): Replace this script with a statically linked native binary so we don't
    #  depend on either /bin/bash being available on the Process host.

    # Note: the backslash after the """ marker ensures that the shebang is at the start of the
    # script file. Many OSs will not see the shebang if there is intervening whitespace.
    script_path = "./script.sh"
    script_content = dedent(
        """\
        #!/usr/bin/env bash

        set -euo pipefail

        if command -v which > /dev/null; then
            command which -a $1
        else
            command -v $1
        fi
        """
    )
    script_digest = await Get(
        Digest,
        CreateDigest([FileContent(script_path, script_content.encode(), is_executable=True)]),
    )

    search_path = create_path_env_var(request.search_path)
    result = await Get(
        FallibleProcessResult,
        # We use a volatile process to force re-run since any binary found on the host system today
        # could be gone tomorrow. Ideally we'd only do this for local processes since all known
        # remoting configurations include a static container image as part of their cache key which
        # automatically avoids this problem.
        UncacheableProcess(
            Process(
                description=f"Searching for `{request.binary_name}` on PATH={search_path}",
                level=LogLevel.DEBUG,
                input_digest=script_digest,
                argv=[script_path, request.binary_name],
                env={"PATH": search_path},
            ),
            scope=ProcessScope.PER_SESSION,
        ),
    )

    binary_paths = BinaryPaths(binary_name=request.binary_name)
    if result.exit_code != 0:
        return binary_paths

    found_paths = result.stdout.decode().splitlines()
    if not request.test:
        return dataclasses.replace(binary_paths, paths=[BinaryPath(path) for path in found_paths])

    results = await MultiGet(
        Get(
            FallibleProcessResult,
            UncacheableProcess(
                Process(
                    description=f"Test binary {path}.",
                    level=LogLevel.DEBUG,
                    argv=[path, *request.test.args],
                ),
                scope=ProcessScope.PER_SESSION,
            ),
        )
        for path in found_paths
    )
    return dataclasses.replace(
        binary_paths,
        paths=[
            BinaryPath.fingerprinted(path, result.stdout)
            if request.test.fingerprint_stdout
            else BinaryPath(path, result.stdout.decode())
            for path, result in zip(found_paths, results)
            if result.exit_code == 0
        ],
    )