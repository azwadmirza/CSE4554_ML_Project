    async def _run(
        self,
        *args: Any,
        valid_exit_codes: Tuple[int, ...] = (0,),
        debug_only: bool = False,
        **kwargs: Any,
    ) -> CompletedProcess:
        """
        Parameters
        ----------
        valid_exit_codes : tuple
            Specifies valid exit codes, used to determine
            if stderr should be sent as debug or error level in logging.
            When not provided, defaults to :code:`(0,)`
        debug_only : bool
            Specifies if stderr can be sent only as debug level in logging.
            When not provided, defaults to `False`
        """
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env.pop("GIT_ASKPASS", None)
        # attempt to force all output to plain ascii english
        # some methods that parse output may expect it
        # according to gettext manual both variables have to be set:
        # https://www.gnu.org/software/gettext/manual/gettext.html#Locale-Environment-Variables
        env["LC_ALL"] = "C"
        env["LANGUAGE"] = "C"
        kwargs["env"] = env
        async with self._repo_lock:
            p: CompletedProcess = await asyncio.get_running_loop().run_in_executor(
                self._executor,
                functools.partial(sp_run, *args, stdout=PIPE, stderr=PIPE, **kwargs),
            )
            stderr = p.stderr.decode().strip()
            if stderr:
                if debug_only or p.returncode in valid_exit_codes:
                    log.debug(stderr)
                else:
                    log.error(stderr)
            return p