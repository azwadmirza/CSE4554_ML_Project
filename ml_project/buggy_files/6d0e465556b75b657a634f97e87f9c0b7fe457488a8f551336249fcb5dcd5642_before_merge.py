    def _spawn_from_binary_external(cls, binary):
        def create_interpreter(stdout, check_binary=False):
            identity = stdout.decode("utf-8").strip()
            if not identity:
                raise cls.IdentificationError("Could not establish identity of {}.".format(binary))
            interpreter = cls(PythonIdentity.decode(identity))
            # We should not need to check this since binary == interpreter.binary should always be
            # true, but historically this could be untrue as noted in `PythonIdentity.get`.
            if check_binary and not os.path.exists(interpreter.binary):
                raise cls.InterpreterNotFound(
                    "Cached interpreter for {} reports a binary of {}, which could not be found".format(
                        binary, interpreter.binary
                    )
                )
            return interpreter

        # Part of the PythonInterpreter data are environment markers that depend on the current OS
        # release. That data can change when the OS is upgraded but (some of) the installed interpreters
        # remain the same. As such, include the OS in the hash structure for cached interpreters.
        os_digest = hashlib.sha1()
        for os_identifier in platform.release(), platform.version():
            os_digest.update(os_identifier.encode("utf-8"))
        os_hash = os_digest.hexdigest()

        interpreter_cache_dir = os.path.join(ENV.PEX_ROOT, "interpreters")
        os_cache_dir = os.path.join(interpreter_cache_dir, os_hash)
        if os.path.isdir(interpreter_cache_dir) and not os.path.isdir(os_cache_dir):
            with TRACER.timed("GCing interpreter cache from prior OS version"):
                safe_rmtree(interpreter_cache_dir)

        interpreter_hash = CacheHelper.hash(binary)

        # Some distributions include more than one copy of the same interpreter via a hard link (e.g.:
        # python3.7 is a hardlink to python3.7m). To ensure a deterministic INTERP-INFO file we must
        # emit a separate INTERP-INFO for each link since INTERP-INFO contains the interpreter path and
        # would otherwise be unstable.
        #
        # See cls._REGEXEN for a related affordance.
        path_id = binary.replace(os.sep, ".").lstrip(".")

        cache_dir = os.path.join(os_cache_dir, interpreter_hash, path_id)
        cache_file = os.path.join(cache_dir, cls.INTERP_INFO_FILE)
        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "rb") as fp:
                    return SpawnedJob.completed(create_interpreter(fp.read(), check_binary=True))
            except (IOError, OSError, cls.Error, PythonIdentity.Error):
                safe_rmtree(cache_dir)
                return cls._spawn_from_binary_external(binary)
        else:
            pythonpath = third_party.expose(["pex"])
            cmd, env = cls._create_isolated_cmd(
                binary,
                args=[
                    "-c",
                    dedent(
                        """\
                        import os
                        import sys

                        from pex.common import atomic_directory, safe_open
                        from pex.interpreter import PythonIdentity


                        encoded_identity = PythonIdentity.get(binary={binary!r}).encode()
                        sys.stdout.write(encoded_identity)
                        with atomic_directory({cache_dir!r}) as cache_dir:
                            if cache_dir:
                                with safe_open(os.path.join(cache_dir, {info_file!r}), 'w') as fp:
                                    fp.write(encoded_identity)
                        """.format(
                            binary=binary, cache_dir=cache_dir, info_file=cls.INTERP_INFO_FILE
                        )
                    ),
                ],
                pythonpath=pythonpath,
            )
            process = Executor.open_process(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            job = Job(command=cmd, process=process)
            return SpawnedJob.stdout(job, result_func=create_interpreter)